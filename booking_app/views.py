import random
import stripe
from django.db.models import BooleanField, Case, When
from django.db.models.query import QuerySet
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, View, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from .forms import CustomUserCreationForm, ReviewForm, RoomSearchForm, PaymentForm
from .models import (User, Discount, RoomItem, 
                     Booking, Address, RoomBooked, 
                     Review, BookingInfo, EventInfo,
                     Payment)

stripe.api_key = settings.STRIPE_SECRET_KEY

def index(request):
    return render(request, 'index.html')

class UserView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, 'user_profile.html', {'user': request.user})
        else:
            return render(request, 'login.html')

class CreateUserView(CreateView):
    template_name = 'create_user.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('index')
    
class FeaturedRooms(ListView):
    model = RoomItem
    template_name = "room_main_view.html"
    context_object_name = "rooms"
    paginate_by = 8
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(available=True).order_by('?')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured'] = True 
        return context

class UserBookedRoomsView(LoginRequiredMixin, ListView):
    model = RoomBooked
    template_name = "user_booked_rooms.html"
    context_object_name = "booked_rooms"
    paginate_by = 8
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            rooms_booked = RoomBooked.objects.filter(
                booking__user=self.request.user
            ).values_list('id', flat=True)
            
            queryset = queryset.filter(id__in=rooms_booked)
        return queryset
    
class DiscountedRoomsView(ListView):
    model = RoomItem
    template_name = "discounted_rooms.html"
    context_object_name = "discounted_rooms"
    paginate_by = 8
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
            available=True, discount__isnull=False).distinct().order_by('?')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured'] = True 
        return context
    
class RoomDetailView(DetailView):
    model = RoomItem
    template_name = 'room_details.html'
    context_object_name = 'room'
    
class BookingHistoryView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'booking_history.html'
    context_object_name = 'bookings'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user).order_by('-time_placed')
    
class ReviewSubmitView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'review_add.html'
    context_object_name = 'review'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('index')
    
class RoomSearchView(ListView):
    model = RoomItem
    template_name = "room_main_view.html"
    context_object_name = "rooms"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(available=True).order_by('?')

        location = self.request.GET.get('location')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        amenities = self.request.GET.get('amenities')
        availability = self.request.GET.get('availability')

        if location:
            queryset = queryset.filter(description__icontains=location)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if amenities:
            queryset = queryset.filter(description__icontains=amenities)
        if availability:
            queryset = queryset.filter(rooms_available__gt=0)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured'] = True
        context['search_form'] = RoomSearchForm(self.request.GET or None) 
        return context
    
class BookingConfirmView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = "booking_confirm.html"
    context_object_name = "booking"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

class PaymentView(LoginRequiredMixin, View):
    def get(self, request):
        form = PaymentForm()
        return render(request, 'payment.html', {'form': form, 'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY})

    def post(self, request):
        form = PaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            stripe_token = form.cleaned_data['stripe_token']
            
            try:
                charge = stripe.Charge.create(
                    amount=int(amount * 100),
                    currency='usd',
                    source=stripe_token,
                    description='Payment Description'
                )
                
                Payment.objects.create(
                    user=request.user,
                    amount=amount,
                    stripe_charge_id=charge.id,
                    status='Completed'
                )
                return redirect('payment_success')
            except stripe.error.StripeError:
                Payment.objects.create(
                    user=request.user,
                    amount=amount,
                    status='Failed'
                )
                return redirect('payment_failed')

        return render(request, 'payment.html', {'form': form, 'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY})

class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    template_name = "payment_success.html"

class PaymentFailedView(LoginRequiredMixin, TemplateView):
    template_name = "payment_failed.html"

import random
from django.db.models import BooleanField, Case, When
from django.db.models.query import QuerySet
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, View, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from .forms import CustomUserCreationForm, ReviewForm
from .models import (User, Discount, RoomItem, 
                     Booking, Address, RoomBooked, 
                     Review, BookingInfo, EventInfo)


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
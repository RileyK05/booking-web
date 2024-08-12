import stripe
from django.conf import settings
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, View, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from .forms import CustomUserCreationForm, ReviewForm, RoomSearchForm
from .models import (
    User, Discount, RoomItem, Booking, Address, 
    RoomBooked, Review, BookingInfo, EventInfo, Payment, DatesBooked
)


stripe.api_key = settings.STRIPE_SECRET_KEY

def index(request):
    return render(request, 'index.html')

class UserView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, 'user_profile.html', {'user': request.user})
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
        return queryset.filter(available=True).order_by('?')

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
        return queryset.filter(available=True, discount__isnull=False).distinct().order_by('?')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured'] = True
        return context

class RoomDetailView(DetailView):
    model = RoomItem
    template_name = 'room_details.html'
    context_object_name = 'room'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bookings'] = self.object.dates_booked.all()
        return context

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

from django.views.generic import ListView
from .models import RoomItem
from .forms import RoomSearchForm

from django.db.models import Q

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
            queryset = queryset.filter(
                Q(address__street__icontains=location) |
                Q(address__city__icontains=location) |
                Q(address__state__icontains=location) |
                Q(address__country__icontains=location) |
                Q(description__icontains=location)
            )
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if amenities:
            queryset = queryset.filter(description__icontains=amenities)
        if availability:
            queryset = queryset.filter(rooms_available__gt=0)
        
        return queryset


class BookingConfirmView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = "booking_confirm.html"
    context_object_name = "booking"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

class InitiatePaymentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        room = get_object_or_404(RoomItem, pk=pk)
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')

        if not room.is_available(check_in, check_out):
            return JsonResponse({"error": "Selected booking window is not available."}, status=400)

        amount = int(room.price * 100)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': room.title,
                    },
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('payment_failed')),
        )

        booking = Booking.objects.create(
            user=request.user,
            check_in=check_in,
            check_out=check_out,
            stripe_session_id=session.id,
        )

        RoomBooked.objects.create(
            booking=booking,
            room=room,
            price=room.price,
            time_booked=timezone.now(),
            number_of_nights=(timezone.datetime.strptime(check_out, '%Y-%m-%d') - timezone.datetime.strptime(check_in, '%Y-%m-%d')).days
        )

        DatesBooked.objects.create(
            room=room,
            booking=booking,
            check_in=check_in,
            check_out=check_out
        )

        Payment.objects.create(
            user=request.user,
            amount=room.price,
            stripe_charge_id=session.id,
            status='Pending'
        )

        return redirect(session.url, code=303)


class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    template_name = "payment_success.html"

    def get(self, request, *args, **kwargs):
        session_id = request.GET.get('session_id')
        session = stripe.checkout.Session.retrieve(session_id)
        booking = get_object_or_404(Booking, stripe_session_id=session_id)
        booking.payment_status = Booking.ORDER_COMPLETE
        booking.save()

        for room_booked in booking.rooms_booked.all():
            room_booked.room.rooms_available -= 1
            room_booked.room.save()

        return super().get(request, *args, **kwargs)


class PaymentFailedView(LoginRequiredMixin, TemplateView):
    template_name = "payment_failed.html"

    def get(self, request, *args, **kwargs):
        session_id = request.GET.get('session_id')
        booking = None
        if session_id:
            booking = get_object_or_404(Booking, stripe_session_id=session_id)
            booking.payment_status = Booking.ORDER_FAILED
            booking.save()
        return self.render_to_response({'booking': booking})


class BookingWindowsView(LoginRequiredMixin, DetailView):
    model = RoomItem
    template_name = 'booking_windows.html'
    context_object_name = 'room'


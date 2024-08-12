from django.urls import path, include
from .views import (
    index, UserView, CreateUserView, AllRoomsView, 
    UserBookedRoomsView, DiscountedRoomsView, RoomDetailView,
    BookingHistoryView, ReviewSubmitView, RoomSearchView,
    BookingConfirmView, InitiatePaymentView, PaymentSuccessView, 
    PaymentFailedView, BookingWindowsView, FeaturedRoomsInCityView
)

urlpatterns = [
    # Main page
    path('', FeaturedRoomsInCityView.as_view(), name='index'),
    
    # User-related views
    path('user/', UserView.as_view(), name='user_profile'),
    path('create-user/', CreateUserView.as_view(), name='create_user'),

    # Room-related views
    path('rooms/', AllRoomsView.as_view(), name='rooms'),
    path('featured-rooms/', FeaturedRoomsInCityView.as_view(), name='featured_rooms'), 
    path('room/<int:pk>/', RoomDetailView.as_view(), name='room_detail'), 
    path('room/<int:pk>/windows/', BookingWindowsView.as_view(), name='booking_windows'),
    path('user/booked-rooms/', UserBookedRoomsView.as_view(), name='user_booked_rooms'), 
    path('discounted-rooms/', DiscountedRoomsView.as_view(), name='discounted_rooms'), 
    path('search/', RoomSearchView.as_view(), name='room_search'),

    # Booking-related views
    path('booking/history/', BookingHistoryView.as_view(), name='booking_history'), 
    path('booking/confirm/<int:pk>/', BookingConfirmView.as_view(), name='booking_confirm'), 

    # Review-related views
    path('review/add/', ReviewSubmitView.as_view(), name='review_add'), 

    # Payment-related views
    path('payment/<int:pk>/initiate/', InitiatePaymentView.as_view(), name='initiate_payment'), 
    path('payment/success/', PaymentSuccessView.as_view(), name='payment_success'),
    path('payment/failed/', PaymentFailedView.as_view(), name='payment_failed'),

    # Authentication paths
    path('accounts/', include('django.contrib.auth.urls')), 
]

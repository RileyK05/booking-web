from django.urls import path, include
from .views import (
    index, UserView, CreateUserView, FeaturedRooms, 
    UserBookedRoomsView, DiscountedRoomsView, RoomDetailView,
    BookingHistoryView, ReviewSubmitView, RoomSearchView,
    BookingConfirmView, InitiatePaymentView, PaymentSuccessView, 
    PaymentFailedView, BookingWindowsView
)

urlpatterns = [
    path('', index, name='index'),
    path('user/', UserView.as_view(), name='user_profile'),
    path('create-user/', CreateUserView.as_view(), name='create_user'),
    path('featured-rooms/', FeaturedRooms.as_view(), name='featured_rooms'),
    path('user/booked-rooms/', UserBookedRoomsView.as_view(), name='user_booked_rooms'),
    path('discounted-rooms/', DiscountedRoomsView.as_view(), name='discounted_rooms'),
    path('room/<int:pk>/', RoomDetailView.as_view(), name='room_detail'),
    path('booking/history/', BookingHistoryView.as_view(), name='booking_history'),
    path('review/add/', ReviewSubmitView.as_view(), name='review_add'),
    path('search/', RoomSearchView.as_view(), name='room_search'),
    path('booking/confirm/<int:pk>/', BookingConfirmView.as_view(), name='booking_confirm'),
    path('room/<int:pk>/windows/', BookingWindowsView.as_view(), name='booking_windows'),
    
    # Payment paths
    path('payment/<int:pk>/initiate/', InitiatePaymentView.as_view(), name='initiate_payment'),
    path('payment/success/', PaymentSuccessView.as_view(), name='payment_success'),
    path('payment/failed/', PaymentFailedView.as_view(), name='payment_failed'),
    
    # Authentication paths
    path('accounts/', include('django.contrib.auth.urls')),
]

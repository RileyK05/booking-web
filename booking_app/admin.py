from django.contrib import admin, messages
from . import models

@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'get_first_name', 'get_last_name', 'view_bookings', 'get_email', 'profile_rating'
    ]
    ordering = ['first_name', 'last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    @admin.display(description='First Name', ordering='first_name')
    def get_first_name(self, obj):
        return obj.first_name
    
    @admin.display(description='Last Name', ordering='last_name')
    def get_last_name(self, obj):
        return obj.last_name
    
    @admin.display(description='Email')
    def get_email(self, obj):
        return obj.email
    
    @admin.display(description='Bookings')
    def view_bookings(self, obj):
        return ", ".join([str(booking) for booking in obj.bookings.all()])
    
    @admin.display(description='Profile Rating')
    def profile_rating(self, obj):
        return obj.profile_rating or "N/A"


@admin.register(models.RoomItem)
class RoomItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ['title']
    }
    list_display = ['title', 'price', 'rooms_available', 'available']
    list_editable = ['price', 'rooms_available', 'available']
    list_filter = ['available']
    search_fields = ['title', 'description']

    @admin.action(description='Clear Room Availability')
    def clear_availability(self, request, queryset):
        updated_count = queryset.update(rooms_available=0)
        self.message_user(
            request,
            f'{updated_count} rooms were successfully updated',
            messages.WARNING
        ) 

@admin.register(models.Booking)  
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'time_placed', 'check_in', 'check_out', 'payment_status', 'booking_reference'
    ]
    list_filter = ['payment_status', 'time_placed']
    search_fields = ['user__username', 'booking_reference']
    ordering = ['-time_placed']

@admin.register(models.RoomBooked)
class RoomBookedAdmin(admin.ModelAdmin):
    list_display = ['room', 'booking', 'location', 'time_booked', 'number_of_nights', 'total_cost']
    search_fields = ['room__title', 'booking__user__username', 'location__city']
    list_filter = ['time_booked', 'location__city']

@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['room', 'user_reviewing', 'rating', 'description']
    search_fields = ['room__title', 'user_reviewing__username']
    list_filter = ['rating']

@admin.register(models.Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['amount_discounted']
    search_fields = ['amount_discounted']

@admin.register(models.BookingInfo)
class BookingInfoAdmin(admin.ModelAdmin):
    list_display = ['guest_count', 'special_requests']
    search_fields = ['special_requests']

@admin.register(models.EventInfo)
class EventInfoAdmin(admin.ModelAdmin):
    list_display = ['event_name', 'event_date', 'room', 'discount']
    search_fields = ['event_name', 'room__title']
    list_filter = ['event_date']

@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'status', 'timestamp']
    search_fields = ['user__username', 'stripe_charge_id']
    list_filter = ['status', 'timestamp']
    ordering = ['-timestamp']

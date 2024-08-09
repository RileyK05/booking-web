from django.contrib import admin, messages
from . import models

@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'get_first_name', 'get_last_name', 'view_bookings', 'get_email'
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
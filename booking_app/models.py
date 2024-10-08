from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from uuid import uuid4


class Address(models.Model):
    street = models.CharField(max_length=60)
    city = models.CharField(max_length=60)
    state = models.CharField(max_length=60, null=True, blank=True)
    country = models.CharField(max_length=60)
    postal_code = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.country}"


class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    profile_rating = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    addresses = models.ManyToManyField(Address, through='UserAddress', related_name='users')

    def __str__(self):
        return self.username


class UserAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'address')

    def __str__(self):
        return f"{self.user.username} - {self.address}"


class Discount(models.Model):
    amount_discounted = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"Discount: {self.amount_discounted}"


class RoomItem(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    available = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    discount = models.ManyToManyField(Discount, blank=True, related_name="room_items")
    number_of_rooms = models.PositiveIntegerField(default=1)
    rooms_available = models.PositiveIntegerField(default=1)
    address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name="room_items")
    room_pictures = models.ImageField(upload_to='rooms/', null=True, blank=True)
    
    def is_available(self, check_in, check_out):
        overlapping_bookings = self.dates_booked.filter(
            check_in__lt=check_out,
            check_out__gt=check_in
        )
        return not overlapping_bookings.exists()

    def __str__(self) -> str:
        return self.title


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="bookings")
    time_placed = models.DateTimeField(auto_now=True)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    booking_reference = models.UUIDField(default=uuid4, editable=False, unique=True)
    stripe_session_id = models.CharField(max_length=255, null=True, blank=True) 

    ORDER_PENDING = 'P'
    ORDER_COMPLETE = 'C'
    ORDER_FAILED = 'F'
    
    PAYMENT_STATUS_CHOICES = [
        (ORDER_PENDING, 'Pending'),
        (ORDER_COMPLETE, 'Complete'),
        (ORDER_FAILED, 'Failed'),
    ]
    
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=ORDER_PENDING
    )
    
    def __str__(self):
        return f"Booking {self.id} by {self.user.username} - {self.get_payment_status_display()}"

    
class DatesBooked(models.Model):
    room = models.ForeignKey(RoomItem, on_delete=models.CASCADE, related_name="dates_booked")
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="dates_booked")
    check_in = models.DateField()
    check_out = models.DateField()

    class Meta:
        unique_together = ('room', 'check_in', 'check_out')
        indexes = [
            models.Index(fields=['room', 'check_in', 'check_out']),
        ]

    def __str__(self):
        return f"Room {self.room.title} booked from {self.check_in} to {self.check_out}"


class RoomBooked(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name="rooms_booked")
    room = models.ForeignKey(RoomItem, on_delete=models.PROTECT, related_name="bookings")
    price = models.DecimalField(max_digits=6, decimal_places=2)
    time_booked = models.DateTimeField()
    number_of_nights = models.PositiveIntegerField()

    def total_cost(self):
        return self.number_of_nights * self.price

    def __str__(self):
        return f"Room {self.room.title} booked for {self.booking.user.username}"

class Review(models.Model):
    room = models.ForeignKey(RoomItem, on_delete=models.CASCADE, related_name="reviews")
    description = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    user_reviewing = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_written")
    
    class Meta:
        unique_together = ('room', 'user_reviewing')

    def __str__(self):
        return f"Review for {self.room.title} by {self.user_reviewing.username}"


class BookingInfo(models.Model):
    special_requests = models.TextField(null=True, blank=True)
    guest_count = models.PositiveIntegerField(default=1)
    id = models.UUIDField(primary_key=True, default=uuid4)

    def __str__(self):
        return f"Booking Info"


class EventInfo(models.Model):
    event_name = models.CharField(max_length=255)
    event_date = models.DateField()
    event_description = models.TextField(null=True, blank=True)
    room = models.ForeignKey(RoomItem, on_delete=models.CASCADE, related_name="events")
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True, related_name="events")
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    
    def __str__(self):
        return f"Event {self.event_name} on {self.event_date}"


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_charge_id = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed')])

    def __str__(self):
        return f'Payment {self.id} - {self.status}'

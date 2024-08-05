from django.db.models import BooleanField, Case, When
from django.db.models.query import QuerySet
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, View, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from .forms import CustomUserCreationForm
from .models import (User, Discount, RoomItem, 
                     Booking, Address, RoomBooked, 
                     Review, BookingInfo)


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
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
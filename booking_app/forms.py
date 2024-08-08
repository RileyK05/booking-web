from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Review

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2',
                  'email', 'first_name', 'last_name')
        
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['room', 'description', 'rating']
        
class RoomSearchForm(forms.Form):
    location = forms.CharField(required=False, max_length=100)
    min_price = forms.DecimalField(required=False, min_value=0.01, decimal_places=2)
    max_price = forms.DecimalField(required=False, min_value=0.01, decimal_places=2)
    amenities = forms.CharField(required=False, max_length=100)
    availability = forms.BooleanField(required=False)
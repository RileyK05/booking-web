from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Review, RoomItem

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 
                  'email', 'profile_picture', 'password1', 'password2')

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['room', 'description', 'rating']

class RoomSearchForm(forms.Form):
    location = forms.CharField(required=False)
    min_price = forms.DecimalField(required=False, min_value=0)
    max_price = forms.DecimalField(required=False, min_value=0)
    amenities = forms.CharField(required=False)
    availability = forms.BooleanField(required=False)

class EditProfileForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_picture']

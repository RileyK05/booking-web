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
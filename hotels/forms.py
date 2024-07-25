from django import forms
from .models import Reservation, RoomServiceRequest, CustomUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['reserved_for']


class RoomServiceRequestForm(forms.ModelForm):
    class Meta:
        model = RoomServiceRequest
        fields = ['room_service']


class CustomUserCreationForm(UserCreationForm):
    private_number = forms.CharField(max_length=20, required=True, help_text='Enter your private number')

    class Meta:
        model = CustomUser
        fields = ('private_number', 'email', 'password1', 'password2')


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput)

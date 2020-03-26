from django.contrib.auth.forms import UserCreationForm
from .models import UserInstagram

class UserInstagramForm(UserCreationForm):
    class Meta:
        model = UserInstagram
        fields = ('username', 'password')

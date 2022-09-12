from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *




#User Registration form - creating basic user model
class CreateUserForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = ['username','first_name','email','password1','password2']
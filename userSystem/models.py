from django.db import models
from django.contrib.auth.models import User
# Create your models here.



#setting email field unique
User._meta.get_field('email')._unique = True
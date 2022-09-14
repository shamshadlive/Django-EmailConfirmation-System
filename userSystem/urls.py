from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),
    path('login', views.user_login , name='login'),
    path('register', views.register, name='register'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('checkUsername',views.checkUsername , name='checkUsername'),
    path('checkEmail',views.checkEmail , name='checkEmail'),

    
]

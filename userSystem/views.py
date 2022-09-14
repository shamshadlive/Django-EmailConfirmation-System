from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login ,logout ,get_user_model
from django.contrib import messages
from .models import *
from .forms import *


from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage

from .token import account_activation_token

from django.http import JsonResponse
import json

# Create your views here.





#check username
def checkUsername(request):

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
      if request.method == 'POST':
        getdata=json.load(request) 
        id = getdata['id']
        user_name = getdata['usernameCheck']
        data = {
            'id': id,
            'is_taken': User.objects.filter(username=user_name).exists(),
             }
        return JsonResponse(data)
    else:
        return redirect('/')

#check email
def checkEmail(request):

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
      if request.method == 'POST':
        getdata=json.load(request) 
        id = getdata['id']
        email_id = getdata['emailCheck']
        data = {
            'id': id,
            'is_taken': User.objects.filter(email=email_id).exists(),
             }
        return JsonResponse(data)
    else:
        return redirect('/')
































#register user
def register(request):

        #get user form
        user_form = CreateUserForm()
       
        if request.method == 'POST':
            user_form = CreateUserForm(request.POST)
          
            #checking both conditions
            if user_form.is_valid():

                user = user_form.save(commit=False)
                user.is_active = False  
                user.save()  

                activateEmail(request, user, user_form.cleaned_data.get('email'))

                messages.success(request, 'Please verify your e-mail to login')
                
                return redirect('login')

            else:

                messages.error(request, 'Please check all the field before submission')
             
      
        context={'user_form': user_form}

        return render(request, 'register.html',context)


#login user
def user_login(request):

        if request.method == 'POST':

            username = request.POST.get('inputUsername') 
            password = request.POST.get('inputPassword') 

            #Authenticate User
            user = authenticate(request, username=username , password=password)

            if user is not None:
                #login approved
                login(request, user)
                return redirect('/')
                
            else:
                #sending error message
                messages.error(request, 'Invalid user details.')
                return render(request, 'login.html')

        return render(request, 'login.html')

#login user
def home(request):


        return render(request, 'home.html')


#send mail format create
def activateEmail(request, user, to_email):
    mail_subject = 'Activate your user account.'
    message = render_to_string('sendMail_Template.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
       pass
    else:
        messages.error(request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')


#activating with link
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid!')
    
    return redirect('login')
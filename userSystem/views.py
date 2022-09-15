from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login ,logout ,get_user_model
from django.contrib import messages
from .models import *
from .forms import *
from django.contrib.auth.models import User

from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from .token import account_activation_token
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
import datetime
from django.urls import reverse
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

#check email whtther taken or not
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

    #For loged users , not access register page
    if request.user.is_authenticated:
        return redirect('/')

    else:
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

    #For loged users , not access register page
    if request.user.is_authenticated:
        return redirect('/')

    else:
        if request.method == 'POST':

            username = request.POST.get('inputUsername') 
            password = request.POST.get('inputPassword') 
            user = authenticate(request, username=username , password=password)
            #sending error message with link
            msg = """
                Please Activate Your account first. 
                <br />
                <a href='{url}'> Resend Mail </a>
                """
            url = reverse("resend_Email")
          
           #checking active state of user if user not acitvated
            if (User.objects.filter(username=username , is_active="0").exists() ):

                 messages.error(request,(msg.format(url=url)))
                 return render(request, 'login.html')
            #Authenticate User
            elif user is not None:
                #login approved
                login(request, user)
                return redirect('/')
                    
            else:
                #sending error message
                messages.error(request, 'Invalid user details.')
                return render(request, 'login.html')

        return render(request, 'login.html')



#login user
#Redirect unauthorized user's from accessing home page
@login_required(login_url='login')
def home(request):


        return render(request, 'home.html')


#Creating email format for sending request
def activateEmail(request, user, to_email):
    mail_subject = 'Activate your user account.'
    message = render_to_string('sendMail_Template.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
        'timestamp':datetime.datetime.now()
    })
    email = EmailMultiAlternatives(
            mail_subject, '', '',  [to_email])
    email.attach_alternative(message, "text/html")
    if email.send():
       pass
    else:
        messages.error(request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')


#here handles the link that user clicked from email for activating
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):

        #making user active
        user.is_active = True
        user.save()

        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('login')
    else:

        messages.error(request, 'Activation link is invalid! ')
    
    return redirect('login')



#Generating reset password email format 
def resetPassword_Email(request, user, to_email):
    mail_subject = 'Reset your password.'
    message = render_to_string('resetPassword_Template.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
        'timestamp':datetime.datetime.now()
    })
    email = EmailMultiAlternatives(
            mail_subject, '', '',  [to_email])
    email.attach_alternative(message, "text/html")

    if email.send():
       pass
    else:
        messages.error(request, f'Problem sending reset email to {to_email}, check if you typed it correctly.')


#here handles the link that user clicked from email for resseting password 
def resetpasswordlink(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):

        #passing user and token to next page for seting password
        context={'token':token,'user':user}
        return render(request, 'setnew_Password.html',context)
    
    else:

        messages.error(request, 'Activation link is invalid!')
    
    return redirect('login')


#setting new resetted password 
def passwordresetconfirm(request, userid, token):
     if request.method == 'POST':
        #cheking is token avaible
        if (token is not None):

            password = request.POST.get('inputPassword') 
            #getting user
            u = User.objects.get(id=userid)

            #setting fetched password
            u.set_password(password)
            u.save()
            messages.success(request, 'Password reseted succesfully , Please login')
            return redirect('login')
        else:
            return redirect('/')
     else:
            return redirect('/')


#resend confirmation mail
def resend_Email(request):

        if request.method == 'POST':
           #getting email
            email = request.POST.get('inputEmail') 
            
            #cheking whether the user is valid
            if (User.objects.filter(email=email).exists() ):

               #checking the state of user 
                if(User.objects.filter(email=email , is_active="1").exists()):

                    msg = """
                    This user is already active please login
                    <br />
                    <a href='{url}'> Login here </a>
                    """
                    url = reverse("login")

                    #already verifed condition
                    messages.error(request, (msg.format(url=url)))
                    return render(request, 'resend_emailConfirmation.html')   

                else:
                
                #not verified condition
                 obj= User.objects.get(email=email)
                 activateEmail(request, obj, email)
                 messages.success(request, "Reverification Mail Has Been sended to your mail id Please verify to login")
                 return redirect('login')    


            #invalid user conditon
            else:
                #sending error message with link
                msg = """
                Sorry this email is not registered 
                <br />
                <a href='{url}'> Regsiter here </a>
                """
                url = reverse("register")
          
                messages.error(request, (msg.format(url=url)))
                return render(request, 'resend_emailConfirmation.html')

        return render(request, 'resend_emailConfirmation.html')



#logout user
def logoutuser(request):
    logout(request)
    return redirect('login')

#reset Password
def reset_Password(request):
        if request.method == 'POST':
           #getting username
            username = request.POST.get('inputUsername') 
            
            #cheking whether the user is valid
            if (User.objects.filter(username=username).exists() ):
                
                 #sending reset link to email
                 obj= User.objects.get(username=username)
                 toemail = obj.email
                 resetPassword_Email(request, obj, toemail)
                 messages.success(request, "Reset Link Mail Has Been sended to your mail id Please verify to Reset")

                 return render(request, 'login.html')     

            #invalid user conditon
            else:
                #sending error message with link
                msg = """
                Sorry this user is not registered 
                <br />
                <a href='{url}'> Regsiter here </a>
                """
                url = reverse("register")
          
                messages.error(request, (msg.format(url=url)))
                return render(request, 'reset_Password.html')

        return render(request, 'reset_Password.html')
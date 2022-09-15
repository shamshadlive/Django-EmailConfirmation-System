# Django-EmailConfirmation-System

 User Login Interface 

![image](https://user-images.githubusercontent.com/73699937/190372901-b02e0988-90db-4296-bed4-5779b89da212.png)

User registration with validation with ajax , javascript , jquery

![image](https://user-images.githubusercontent.com/73699937/190373259-f6b65144-965c-4909-8746-8f40eb0549be.png)

User will be activted only after confirming link that received on mail id

![image](https://user-images.githubusercontent.com/73699937/190373820-59a96a29-c319-4958-a209-fd592e35366c.png)


Token generation for each user in token.py

      from django.contrib.auth.tokens import PasswordResetTokenGenerator
      import six  

      #Dont forgot to install  pip install six
      class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
          def _make_hash_value(self, user, timestamp):
              return (
                  six.text_type(user.pk) + six.text_type(timestamp)  + six.text_type(user.is_active)
              )

      account_activation_token = AccountActivationTokenGenerator()
      
Creating email format for sending request in views.py

    from django.core.mail import EmailMultiAlternatives
    from .token import account_activation_token
    
    
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
            
 
#here handles the link that user clicked from email for activating in views.py

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
    
    
    
    IN settings.py  for sening mail from gmail
    
    # Emailing settings
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_FROM = 'YOUREMAIL@gmail.com'
    EMAIL_HOST_USER = 'YOUREMAIL@gmail.com'
    EMAIL_HOST_PASSWORD = 'YOURPASSWORD'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    PASSWORD_RESET_TIMEOUT = 14400
    
    
Activation mail recieved on mail
    
   ![Screenshot 2022-09-15 153636](https://user-images.githubusercontent.com/73699937/190377056-df24117e-b4f0-47e7-bb32-ac7d1a687efc.png)


 

After confirming we can login , Unauthorised users are blocked from accessing home page

![image](https://user-images.githubusercontent.com/73699937/190376206-ee14564d-17f3-440f-85d6-4f0895760e53.png)


Users can reset their password by clicking reset password link also mail sended to the registered email and set new password

![image](https://user-images.githubusercontent.com/73699937/190376507-9a5fd22c-caf9-4be6-b4f2-d4e2e839a6a1.png)

![image](https://user-images.githubusercontent.com/73699937/190377137-e793a937-2d21-40e3-83d5-dc8c497aa601.png)


This is a perfect user registration and login system that made with DJANGO , BOOTSTRAP ,AJAX ,JQUERY ,JAVASCRIPT ,HTML5 and MYSQL database

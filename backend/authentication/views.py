from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib import auth
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator
from django.contrib import auth



# Create your views here.


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body) # data containes everything sent by the user
        username = data.get('username','')
        # checking for alnum only username
        if not username.isalnum():
            return JsonResponse({'username_error':'username should only contain alpha-numeric characters'}, status=400)
        # checking if username is already in use
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error':'sorry! username in use, choose another'}, status=409)
        return JsonResponse({'username_valid': True}, status=200)
    

class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body) # data containes everything sent by the user
        email = data.get('email','')
        # checking for valid email
        if not validate_email(email):
            return JsonResponse({'email_error':'Email is invalid'}, status=400)
        # checking if username is already in use
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error':'sorry! email in use, choose another'}, status=409)
        return JsonResponse({'email_valid': True}, status=200)

    
class RegistrationView(View):
    # get() request needs to be handled using react
    def post(self, request):
        # get user data
        # validate
        # create user account
        data = json.loads(request.body)
        username = data.get('username','')
        email = data.get('email','')
        password = data.get('password','')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error':'Username already in use'}, status=409)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error':'Email already in use'}, status=409)
        
        if len(password) < 6:
            return JsonResponse({'error':'Password too short'}, status=400)
        
        user = User.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.is_active = False
        user.save()

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        domain = get_current_site(request).domain
        link = reverse('activate', kwargs={'uidb64':uidb64, 'token':token_generator.make_token(user)})
        activate_url = 'http://' + domain + link
        email_subject = 'DevCanvas Account Activation'
        email_body = f'Hi {user.username}, please use this link to verify your account: {activate_url}'
        email_message = EmailMessage(email_subject, email_body, to=[email])
        email_message.send(fail_silently=False)

        return JsonResponse({'message': 'Account created. Please verify your email to activate'}, status=201)



        # if not User.objects.filter(username=username).exists():
        #     if not User.objects.filter(email=email).exists():

        #         if len(password)<6:
        #             messages.error(request, 'Password too short')
        #             return render(request, 'authentication/register.html', context)
                
        #         user = User.objects.create_user(username=username, email=email)
        #         user.set_password(password)
        #         user.is_active = False
        #         user.save()

        #         # path to view
        #         # - getting the domain we are on
        #         # - relative url to Verification
        #         # - encode uid 
        #         # - token
        #         email_subject = 'Activate your account'
                
        #         uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        #         domain = get_current_site(request).domain
        #         link = reverse('activate',kwargs={
        #             'uidb64':uidb64,'token':token_generator.make_token(user)})
        #         activate_url = 'http://'+domain+link
        #         email_body = 'Hi ' + user.username + ' Please use this link to verify your account\n' + activate_url
        #         email = EmailMessage(
        #             email_subject,
        #             email_body,
        #             "noreply@semycolon.com",
        #             [email],
        #         )
        #         email.send(fail_silently=False)
        #         messages.success(request,'Account Succefully Created')
        #         return render(request, 'authentication/register.html')
                

        # return render(request, 'authentication/register.html')

class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id) 

            if not token_generator.check_token(user, token):
                # return redirect('login'+'?message='+'User already activated')
                return JsonResponse({'error':'User already activated'}, status=400)
            
            if user.is_active:
                # return redirect('login')
                return JsonResponse({'message':'Account already active'}, status=200)
            
            user.is_active = True
            user.save()
            return JsonResponse({'message':'Account activated successfully'}, status=200)
            # messages.success(request, 'Account activated successfully')
            # return redirect('login')
        except Exception as ex:
            return JsonResponse({'error':'Activation Failed'}, status=400)
        #     pass        
        # return redirect('login')


class LoginView(View):
    # for get(), react only shd redirect appropriately
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username','')
        password = data.get('password','')

        user = auth.authenticate(username=username, password=password)
        if user:
            if user.is_active:
                auth.login(request, user)
                # messages.success(request, 'Welcome, ' + 
                #                     user.username + 'You are now logged in')
                return JsonResponse({'message': f'Welcome {user.username}, you are now logged in'}, status=200)
            
            return JsonResponse({'error':'Account is not active. Please check your registered email'}, status=403)
            # messages.error(request, 'Account is not active. Please check your registered email') 
            # return render(request, 'authentication/login.html')
        return JsonResponse({'error':'Invalid Credentials! Try again'}, status=400)
        # messages.error(request, 'Invalid Credentials! Try again') 
        # return render(request, 'authentication/login.html')
    
    # messages.error(request, 'Please fill all fields!') 
    # return render(request, 'authentication/login.html')


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        return JsonResponse({'message':'You have been logged out'}, status=200)
        # messages.success(request, 'You have been logged out')
        # return redirect('login')

from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import Response
from django.contrib.auth.models import User
from django.http import Response
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
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


# Create your views here.


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body) # data containes everything sent by the user
        username = data.get('username','')
        # checking for alnum only username
        if not username.isalnum():
            return Response({'username_error':'username should only contain alpha-numeric characters'}, status = status.HTTP_400_BAD_REQUEST)
        # checking if username is already in use
        if User.objects.filter(username=username).exists():
            return Response({'username_error':'sorry! username in use, choose another'}, status=status.HTTP_409_CONFLICT)
        return Response({'username_valid': True}, status=status.HTTP_200_OK)
    

class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body) # data containes everything sent by the user
        email = data.get('email','')
        # checking for valid email
        if not validate_email(email):
            return Response({'email_error':'Email is invalid'}, status = status.HTTP_400_BAD_REQUEST)
        # checking if username is already in use
        if User.objects.filter(email=email).exists():
            return Response({'email_error':'sorry! email in use, choose another'}, status=status.HTTP_409_CONFLICT)
        return Response({'email_valid': True}, status=status.HTTP_200_OK)

    
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
            return Response({'error':'Username already in use'}, status=status.HTTP_409_CONFLICT)
        
        if User.objects.filter(email=email).exists():
            return Response({'error':'Email already in use'}, status=status.HTTP_409_CONFLICT)
        
        if len(password) < 6:
            return Response({'error':'Password too short'}, status = status.HTTP_400_BAD_REQUEST)
        
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

        return Response({'message': 'Account created. Please verify your email to activate'}, status=status.HTTP_201_CREATED)



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
                return Response({'error':'User already activated'}, status = status.HTTP_400_BAD_REQUEST)
            
            if user.is_active:
                # return redirect('login')
                return Response({'message':'Account already active'}, status=status.HTTP_200_OK)
            
            user.is_active = True
            user.save()
            return Response({'message':'Account activated successfully'}, status=status.HTTP_200_OK)
            # messages.success(request, 'Account activated successfully')
            # return redirect('login')
        except Exception as ex:
            return Response({'error':'Activation Failed'}, status = status.HTTP_400_BAD_REQUEST)
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
                return Response({'message': f'Welcome {user.username}, you are now logged in'}, status=status.HTTP_200_OK)
            
            return Response({'error':'Account is not active. Please check your registered email'}, status=status.HTTP_403_FORBIDDEN)
            # messages.error(request, 'Account is not active. Please check your registered email') 
            # return render(request, 'authentication/login.html')
        return Response({'error':'Invalid Credentials! Try again'}, status = status.HTTP_400_BAD_REQUEST)
        # messages.error(request, 'Invalid Credentials! Try again') 
        # return render(request, 'authentication/login.html')
    
    # messages.error(request, 'Please fill all fields!') 
    # return render(request, 'authentication/login.html')


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        return Response({'message':'You have been logged out'}, status=status.HTTP_200_OK)
        # messages.success(request, 'You have been logged out')
        # return redirect('login')

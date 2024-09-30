from django.shortcuts import render, redirect
from django.views import View
import json
from rest_framework.response import Response
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
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

# Import the serializers
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserVerificationSerializer


### UsernameValidationView
class UsernameValidationView(APIView):
    def get(self, request):
        username = request.GET.get('username', '')
        if not username.isalnum():
            return Response({'username_error': 'Username should only contain alphanumeric characters'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'username_error': 'Sorry! Username in use, choose another'}, status=status.HTTP_409_CONFLICT)
        return Response({'username_valid': True}, status=status.HTTP_200_OK)

    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username', '')
        if not username.isalnum():
            return Response({'username_error': 'Username should only contain alphanumeric characters'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'username_error': 'Sorry! Username in use, choose another'}, status=status.HTTP_409_CONFLICT)
        return Response({'username_valid': True}, status=status.HTTP_200_OK)


### EmailValidationView
class EmailValidationView(APIView):
    def get(self, request):
        email = request.GET.get('email', '')
        if not validate_email(email):
            return Response({'email_error': 'Email is invalid'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'email_error': 'Sorry! Email in use, choose another'}, status=status.HTTP_409_CONFLICT)
        return Response({'email_valid': True}, status=status.HTTP_200_OK)

    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email', '')
        if not validate_email(email):
            return Response({'email_error': 'Email is invalid'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'email_error': 'Sorry! Email in use, choose another'}, status=status.HTTP_409_CONFLICT)
        return Response({'email_valid': True}, status=status.HTTP_200_OK)


### RegistrationView (Only POST Required)
class RegistrationView(APIView):
    def post(self, request):
        data = json.loads(request.body)
        serializer = UserRegistrationSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            link = reverse('activate', kwargs={'uidb64': uidb64, 'token': token_generator.make_token(user)})
            activate_url = 'http://' + domain + link
            email_subject = 'DevCanvas Account Activation'
            email_body = f'Hi {user.username}, please use this link to verify your account: {activate_url}'
            email_message = EmailMessage(email_subject, email_body, to=[serializer.validated_data['email']])
            email_message.send(fail_silently=False)
            return Response({'message': 'Account created. Please verify your email to activate'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


### VerificationView (GET method only)
class VerificationView(APIView):
    def get(self, request, uidb64, token):
        serializer = UserVerificationSerializer(data={'uidb64': uidb64, 'token': token})

        if serializer.is_valid():
            uidb64 = serializer.validated_data['uidb64']
            token = serializer.validated_data['token']

            try:
                id = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=id)

                if not token_generator.check_token(user, token):
                    return Response({'error': 'User already activated'}, status=status.HTTP_400_BAD_REQUEST)

                if user.is_active:
                    return Response({'message': 'Account already active'}, status=status.HTTP_200_OK)

                user.is_active = True
                user.save()
                return Response({'message': 'Account activated successfully'}, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({'error': 'Activation Failed'}, status=status.HTTP_400_BAD_REQUEST)


### LoginView
class LoginView(APIView):
    def post(self, request):
        data = json.loads(request.body)
        serializer = UserLoginSerializer(data=data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    return Response({'message': f'Welcome {user.username}, you are now logged in'}, status=status.HTTP_200_OK)
                return Response({'error': 'Account is not active. Please check your registered email'}, status=status.HTTP_403_FORBIDDEN)
            return Response({'error': 'Invalid Credentials! Try again'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


### LogoutView (POST only)
class LogoutView(APIView):
    def post(self, request):
        auth.logout(request)
        return Response({'message': 'You have been logged out'}, status=status.HTTP_200_OK)

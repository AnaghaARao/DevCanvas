from django.shortcuts import render, redirect
from django.views import View
import json
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
# from .models import CustomUser as User
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
from rest_framework_simplejwt.tokens import RefreshToken


# **Import the serializers**
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserVerificationSerializer

# Create your views here.

class UsernameValidationView(APIView):
    def post(self, request):
        data = json.loads(request.body)  # data contains everything sent by the user
        username = data.get('username', '')
        # checking for alnum only username
        if not username.isalnum():
            return Response({'username_error': 'username should only contain alpha-numeric characters'}, status=status.HTTP_400_BAD_REQUEST)
        # checking if username is already in use
        if User.objects.filter(username=username).exists():
            return Response({'username_error': 'sorry! username in use, choose another'}, status=status.HTTP_409_CONFLICT)
        return Response({'username_valid': True}, status=status.HTTP_200_OK)

class EmailValidationView(APIView):
    def post(self, request):
        data = json.loads(request.body)  # data contains everything sent by the user
        email = data.get('email', '')
        # checking for valid email
        if not validate_email(email):
            return Response({'email_error': 'Email is invalid'}, status=status.HTTP_400_BAD_REQUEST)
        # checking if username is already in use
        if User.objects.filter(email=email).exists():
            return Response({'email_error': 'sorry! email in use, choose another'}, status=status.HTTP_409_CONFLICT)
        return Response({'email_valid': True}, status=status.HTTP_200_OK)

class RegistrationView(APIView):
    def post(self, request):
        # **Use the serializer for registration**
        data = json.loads(request.body)
        serializer = UserRegistrationSerializer(data=data)  # **Serializer for registration**
        
        if serializer.is_valid():
            user = serializer.save()
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            frontend_domain = 'localhost:5173'
            link = reverse('activate', kwargs={'uidb64': uidb64, 'token': token_generator.make_token(user)})
            activate_url = 'http://' + frontend_domain + link
            email_subject = 'DevCanvas Account Activation'
            email_body = f'Hi {user.username}, please use this link to verify your account: {activate_url}'
            email_message = EmailMessage(email_subject, email_body, to=[serializer.validated_data['email']])  # **Use validated email**
            email_message.send(fail_silently=False)
            return Response({'message': 'Account created. Please verify your email to activate'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            # user.auth_token = token  # Save the token in the user model
            user.save()

            return Response({'message': 'Account activated successfully'}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'error': 'Activation Failed'}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        data = json.loads(request.body)
        serializer = UserLoginSerializer(data=data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            try:
                # First, check if the user with the given username exists
                user = User.objects.get(username=username)

                # Check if the password is correct
                if check_password(password, user.password):
                    if user.is_active:
                        # If user is active, log them in and generate tokens
                        auth.login(request, user)
                        refresh = RefreshToken.for_user(user)
                        return Response({
                            'message': f'Welcome {user.username}, you are now logged in',
                            'access': str(refresh.access_token),  # Include access token
                            'refresh': str(refresh),  # Include refresh token
                        }, status=status.HTTP_200_OK)
                    else:
                        # If user is inactive, send a message to activate the account
                        return Response(
                            {'error': 'Account is not active. Please check your registered email to activate your account.'},
                            status=status.HTTP_403_FORBIDDEN
                        )
                else:
                    # If password is incorrect, return an invalid credentials message
                    return Response({'error': 'Invalid Credentials! Try again'}, status=status.HTTP_400_BAD_REQUEST)

            except User.DoesNotExist:
                # If the user doesn't exist, return an invalid credentials message
                return Response({'error': 'Invalid Credentials! Try again'}, status=status.HTTP_400_BAD_REQUEST)
        
        # If serializer is invalid, return validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request):
        auth.logout(request)
        return Response({'message': 'You have been logged out'}, status=status.HTTP_200_OK)

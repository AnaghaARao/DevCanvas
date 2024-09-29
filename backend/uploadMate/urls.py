from django.urls import path
from . import views

urlpatterns = [
    path('upload/',views.upload_codebase, name='upload_codebase'),
]
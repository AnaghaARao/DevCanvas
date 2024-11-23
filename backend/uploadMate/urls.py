from django.urls import path
from . import views

urlpatterns = [
    path('uplink/',views.upload_codebase, name='uplink'),
    path('history/', views.history, name='history'),
]
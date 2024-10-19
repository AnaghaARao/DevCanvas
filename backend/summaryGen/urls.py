from django.urls import path
from .views import generate_summary_view

urlpatterns = [
    # Map the URL to the generate_summary_view
    path('generate-summary/', generate_summary_view, name='generate_summary'),
]

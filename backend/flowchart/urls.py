from django.urls import path
from .views import generate_flowchart_view

urlpatterns = [
    # Map the URL to the generate_summary_view
    path('generate-flowchart/<int:doc_id>/', generate_flowchart_view, name='gen-flowchart'),
]
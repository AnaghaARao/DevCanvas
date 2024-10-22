from django.urls import path
from .views import generate_class_diagram_view

urlpatterns = [
    # Map the URL to the generate_summary_view
    path('generate-class-diagram/<int:doc_id>/', generate_class_diagram_view, name='gen-class-diagram'),
]

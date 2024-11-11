from django.urls import path
from .views import generate_sequence_diagram_view

urlpatterns = [
    # Map the URL to the generate_summary_view
    path('generate-sequence-diagram/<int:doc_id>/', generate_sequence_diagram_view, name='gen-sequence-diagrm'),
]
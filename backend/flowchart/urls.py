from django.urls import path
from .views import generate_flowchart_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Map the URL to the generate_summary_view
    path('generate-flowchart/<int:doc_id>/', generate_flowchart_view, name='gen-flowchart'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import FileNest
from .serializers import DocumentUploadSerializer
from django.http import JsonResponse
import os

from summaryGen.views import generate_summary_view

# Create your views here.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_codebase(request):
    if request.method == 'POST':
        data = request.data.copy()  # Make a copy of request data
        data['author'] = request.user.username  # Automatically assign the logged-in user's username

        serializer = DocumentUploadSerializer(data=request.data)
        if serializer.is_valid():
            doc_upload = serializer.save()

           # Check for the uploaded file
            file = request.FILES.get('file')
            if not file:
                return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

            # Define allowed extensions for Python files
            allowed_extensions = ['.py', '.pyw','.java']

            # Get the file extension
            file_extension = os.path.splitext(file.name)[1]  # Use os.path.splitext to get the extension

            # Check if the file extension is allowed
            if file_extension not in allowed_extensions:
                return Response({'error': 'Unsupported file type'}, status=status.HTTP_400_BAD_REQUEST)
            
            # send response based on docType
            if doc_upload.docType == 'summary':
                return Response({'redirect':'/summaryGen/generate-summary/', 'doc_id':doc_upload.id}, status=status.HTTP_201_CREATED)
            elif doc_upload.docType == 'class diagram':
                return Response({'redirect':'classDiagram', 'doc_id':doc_upload.id}, status=status.HTTP_201_CREATED)
            elif doc_upload.docType == 'sequence diagram':
                return Response({'redirect':'sequenceDiagram', 'doc_id':doc_upload.id}, status=status.HTTP_201_CREATED)
            elif doc_upload.docType == 'flowchart':
                return Response({'redirect':'flowchart', 'doc_id':doc_upload.id}, status=status.HTTP_201_CREATED)            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            

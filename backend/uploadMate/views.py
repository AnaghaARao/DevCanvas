from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import FileNest
from .serializers import DocumentUploadSerializer
from django.http import JsonResponse
import os

# Create your views here.
@api_view(['POST'])
def upload_codebase(request):
    if request.method == 'POST':
        serializer = DocumentUploadSerializer(data=request.data)
        if serializer.is_valid():
            doc_upload = serializer.save()

           # Check for the uploaded file
            file = request.FILES.get('file')
            if not file:
                return Response({'error': 'No file uploaded'}, status=400)

            # Define allowed extensions for Python files
            allowed_extensions = ['.py', '.pyw']

            # Get the file extension
            file_extension = os.path.splitext(file.name)[1]  # Use os.path.splitext to get the extension

            # Check if the file extension is allowed
            if file_extension not in allowed_extensions:
                return Response({'error': 'Unsupported file type'}, status=400)
            
            # send response based on docType
            if doc_upload.docType == 'summary':
                return Response({'redirect':'summary_app', 'doc_id':doc_upload.id}, status=201)
            elif doc_upload.docType == 'UML diagram':
                return Response({'redirect':'uml_app', 'doc_id':doc_upload.id}, status=201)
            else:
                return Response({'message':'Upload Successful, no specific route'}, status=201)
            
        return Response(serializer.errors, status=400)
            

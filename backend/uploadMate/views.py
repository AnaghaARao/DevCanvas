from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import FileNest
from .serializers import DocumentUploadSerializer
from django.http import JsonResponse
import os
from django.http import HttpRequest
from django.test import Client
from django.urls import reverse

from summaryGen.views import generate_summary_view
from classDiagram.views import generate_class_diagram_view
from sequenceDiagram.views import generate_sequence_diagram_view
from flowchart.views import generate_flowchart_view

# Create your views here.
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def upload_codebase(request):
    if request.method == 'POST':
        # data = request.data.copy()  # Make a copy of request data
        # data['author'] = request.user.username  # Automatically assign the logged-in user's username

        serializer = DocumentUploadSerializer(data=request.data)
        if serializer.is_valid():
            doc_upload = serializer.save()

           # Check for the uploaded file
            files = request.FILES.getlist('files')
            if not files:
                return Response({'error': 'No files uploaded'}, status=status.HTTP_400_BAD_REQUEST)
            
            is_dir = len(files)>1

            # Define allowed extensions for Python files
            allowed_extensions = ['.py', '.pyw','.java']

            for file in files:
                # Get the file extension
                file_extension = os.path.splitext(file.name)[1]  # Use os.path.splitext to get the extension

                # Check if the file extension is allowed
                if file_extension not in allowed_extensions:
                    return Response({'error': f'Unsupported file type for file {file}'}, status=status.HTTP_400_BAD_REQUEST)
                
            if is_dir:
                # Logic to save directory details, such as creating a unique identifier for the directory itself
                doc_upload.doc_id = f"dir_{doc_upload.id}"  # Example identifier for directories
                doc_upload.is_directory = True 
            
            raw_request = HttpRequest()
            raw_request.method = request.method
            raw_request.POST = request.data
            # send response based on docType
            if doc_upload.docType == 'summary':
                response = generate_summary_view(raw_request, doc_upload.id)
                if 'file_url' in response.data:
                    print(response.data['file_url'])
                else:
                    print("file_url not found in response:", response.data)
                return Response(response.data, status=response.status_code)
                # to call django.http response object instead of rest_framework response object
                # response = generate_summary_view(request, doc_id = doc_upload.id)
                # client = Client()
                # summary_url = client.post(reverse('summary-gen', kwargs={'doc_id':doc_upload.id})) # reverse url for summary generation
                # response = client.post(summary_url, data={}) # make internal post request
                # return Response(response.json(), status = response.status_code) # return response from summary generator
                # response = generate_summary_view(request, doc_upload.id)
                # return Response(response.data, status=response.status_code)                
            elif doc_upload.docType == 'class diagram':
                response = generate_class_diagram_view(raw_request, doc_upload.id)
                if 'file_url' in response.data:
                    print(response.data['file_url'])
                else:
                    print("file_url not found in response:", response.data)
                return Response(response.data, status=response.status_code)
            elif doc_upload.docType == 'sequence diagram':
                response = generate_sequence_diagram_view(raw_request, doc_upload.id)
                if 'file_url' in response.data:
                    print(response.data['file_url'])
                else:
                    print("file_url not found in response:", response.data)
                return Response(response.data, status=response.status_code)
            elif doc_upload.docType == 'flowchart':
                response = generate_flowchart_view(raw_request, doc_upload.id)
                if 'file_url' in response.data:
                    print(response.data['file_url'])
                else:
                    print("file_url not found in response:", response.data)
                return Response(response.data, status=response.status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            

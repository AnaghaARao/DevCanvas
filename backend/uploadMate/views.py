from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import FileNest, FileEntry
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
# Helper function to handle the upload of files
def handle_file_uploads(files, dir_name, author, doc_type, language):
    file_nest = FileNest.objects.create(
        language=language,  # you can set this dynamically based on your requirement
        author=author,
        docType=doc_type,
        dir_name=dir_name
    )

    for file in files:
        FileEntry.objects.create(
            file_nest=file_nest,
            file=file
        )

    return file_nest

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def upload_codebase(request):
    if request.method == 'POST':
        print("request: ", request.data)
        print("Files:", request.FILES)
        # data = request.data.copy()  # Make a copy of request data
        # data['author'] = request.user.username  # Automatically assign the logged-in user's username
        # print("request: ",request.data)
        serializer = DocumentUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Get the directory name and files from the request
            dir_name = serializer.validated_data.get('dir_name')
            author = serializer.validated_data.get('author')
            doc_type = serializer.validated_data.get('docType')
            language = serializer.validated_data.get('language')

            # Get the files uploaded (the 'files[]' field contains the list of files)
            files = request.FILES.getlist('files[]')
            print("request: ", request.data)
            print("Files:", request.FILES)

            # Validate files are provided
            if not files:
                return Response({'error': 'No files uploaded'}, status=status.HTTP_400_BAD_REQUEST)

            # Process the file upload and create FileNest and FileEntry objects
            doc_upload = handle_file_uploads(files, dir_name, author, doc_type, language)

            # Define allowed extensions for Python files
            allowed_extensions = ['.py', '.pyw','.java']

            for file in files:
                # Get the file extension
                file_extension = os.path.splitext(file.name)[1]  # Use os.path.splitext to get the extension

                # Check if the file extension is allowed
                if file_extension not in allowed_extensions:
                    return Response({'error': f'Unsupported file type for file {file}'}, status=status.HTTP_400_BAD_REQUEST)
            
            doc_upload.doc_id = f"dir_{doc_upload.id}"  # Example identifier for directories
            
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
        else:
            print('Invalid serializer')
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            

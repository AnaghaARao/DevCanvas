from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import DocumentUploadSerializer
from summaryGen.views import generate_summary_view
from classDiagram.views import generate_class_diagram_view
from sequenceDiagram.views import generate_sequence_diagram_view
from flowchart.views import generate_flowchart_view
from django.http import HttpRequest
import os
import shutil
from django.conf import settings
from datetime import datetime

# Helper to call appropriate generator view
def call_generator_view(doc_type, request, doc_id):
    view_mapping = {
        'summary': generate_summary_view,
        'class diagram': generate_class_diagram_view,
        'sequence diagram': generate_sequence_diagram_view,
        'flowchart': generate_flowchart_view
    }
    return view_mapping[doc_type](request, doc_id)

@api_view(['POST'])
def upload_codebase(request):
    if request.method == 'POST':
        print("request: ", request.data)
        serializer = DocumentUploadSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            doc_upload = serializer.save()  # Save FileNest and associated FileEntry instances

            # Prepare raw request for generator view
            raw_request = HttpRequest()
            raw_request.method = request.method
            raw_request.POST = request.data

            # Call the documentation generator view
            response = call_generator_view(doc_upload.docType, raw_request, doc_upload.id)
            if 'file_url' in response.data:
                print(response.data['file_url'])
            else:
                print("file_url not found in response:", response.data)

            delete_folders_except_results(doc_upload.author)

            return Response(response.data, status=response.status_code)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def history(request):
    if request.method == 'POST':
        author = request.data.get('author', None)
        if not author:
            return Response({'error': 'Author is required'}, status=400)

        results_dir = os.path.join(settings.MEDIA_ROOT, author, 'results')

        if not os.path.exists(results_dir):
            return Response({'error': 'No results found for this author'}, status=404)

        files = []
        for file_name in os.listdir(results_dir):
            file_path = os.path.join(results_dir, file_name)
            if os.path.isfile(file_path):
                # Get the file's last modification time
                date_of_generation = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                files.append({
                    'file_url': f"{settings.MEDIA_URL}{author}/results/{file_name}",
                    'file_name': file_name,
                    'dateOfGeneration': date_of_generation,
                })

        return Response({'files': files}, status=200)



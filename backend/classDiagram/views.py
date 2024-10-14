from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ClassDiagram
from uploadMate.models import FileNest  # Import FileNest model to fetch uploaded code file
from django.conf import settings
from django.core.files import File  # Import Django's File object
import os

# Import the class diagram generation utility function
from .utils import process_file

@api_view(['POST'])
def generate_class_diagram_view(request):
    if request.method == 'POST':
        doc_ids = request.data.getlist('doc_ids')
        if not doc_ids:
            return Response({'error': 'doc_ids are required to fetch the uploaded files'}, status=400)
        
        class_diagram_paths = []

        for doc_id in doc_ids:
            try:
                file_nest = FileNest.objects.get(id=doc_id)
            except FileNest.DoesNotExist:
                return Response({'error': f'Uploaded file with id {doc_id} not found'}, status=404)

            uploaded_file_path = file_nest.file.path
            author = file_nest.author
            language = file_nest.language

            # Call process_file to handle generation and file management
            class_diagram_path = process_file(uploaded_file_path, language, author, doc_id)

            if class_diagram_path is None:
                return Response({'error': f'Class diagram generation failed for {language}'}, status=500)

            # Store the class diagram in the database
            with open(class_diagram_path, 'rb') as generated_file:
                class_diagram = ClassDiagram.objects.create(
                    language=language,
                    author=author
                )
                class_diagram.file.save(os.path.basename(class_diagram_path), File(generated_file), save=True)

            class_diagram_paths.append(class_diagram_path)

        return Response({
            'message': 'Class diagrams generated successfully',
            'class_diagram_paths': class_diagram_paths
        }, status=201)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ClassDiagramSerializer
from .models import ClassDiagram
from uploadMate.models import FileNest  # Import FileNest model to fetch uploaded code file
from django.conf import settings
from django.core.files import File  # Import Django's File object
import os

# Placeholder import for actual class generation function
from .utils import generate_class_diagram

@api_view(['POST'])
def generate_class_diagram(request):
    if request.method == 'POST':
        # Extract doc_id to retrieve the uploaded file from FileNest model
        doc_id = request.data.get('doc_id')
        if not doc_id:
            return Response({'error': 'doc_id is required to fetch the uploaded file'}, status=400)
        
        # Fetch the file uploaded in uploadMate app using FileNest
        try:
            file_nest = FileNest.objects.get(id=doc_id)
        except FileNest.DoesNotExist:
            return Response({'error': 'Uploaded file not found'}, status=404)

        # Get the uploaded file path
        uploaded_file_path = file_nest.file.path  # Full path to the uploaded file
        author = file_nest.author
        language = file_nest.language

        # Generate the class diagram
        class_output_path = generate_class_diagram(uploaded_file_path)  # Pass the uploaded file path to the Class generator

        # Create a path to store the class diagram at uploads/<author>/
        class_storage_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', author)
        os.makedirs(class_storage_dir, exist_ok=True)
        class_output_file_path = os.path.join(class_storage_dir, os.path.basename(class_output_path))

        # Open the generated diagram as a file
        with open(class_output_file_path, 'rb') as generated_file:
            # Store the class diagram in classDiagram model
            class_diagram = ClassDiagram.objects.create(
                language=language,
                author=author
            )
            class_diagram.file.save(os.path.basename(class_output_file_path), File(generated_file), save=True)  # Save the file to FileField

        # Return response with the path to the generated class diagram
        return Response({
            'message': 'Class diagram generated successfully',
            'class_diagram_path': class_output_file_path
        }, status=201)

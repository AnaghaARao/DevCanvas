from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ClassDiagramSerializer
from .models import ClassDiagram
from uploadMate.models import FileNest  # Import FileNest model to fetch uploaded code file
from django.conf import settings
import os

# Placeholder import for actual UML generation function
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

        # Generate the UML diagram
        class_output_path = generate_class_diagram(uploaded_file_path)  # Pass the uploaded file path to the Class generator

        # Create a path to store the UML diagram at uploads/<author>/
        class_storage_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', author)
        os.makedirs(class_storage_dir, exist_ok=True)
        class_output_file_path = os.path.join(class_storage_dir, os.path.basename(class_output_path))

        # Store the UML diagram in UMLDiagram model
        class_diagram = ClassDiagram.objects.create(
            language=language,
            author=author,
            file=class_output_file_path  # Save the generated UML diagram path
        )

        # Return response with the path to the generated UML diagram
        return Response({
            'message': 'UML diagram generated successfully',
            'uml_diagram_path': class_output_file_path
        }, status=201)

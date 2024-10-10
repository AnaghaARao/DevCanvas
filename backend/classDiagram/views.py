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
        original_file_name = os.path.basename(uploaded_file_path)

        # Generate the class diagram using the utility function
        class_output_path = process_file(uploaded_file_path, language)  # Pass the uploaded file path and language to the generator

        if class_output_path is None:
            return Response({'error': f'Class diagram generation failed for {language}'}, status=500)

        # Create a path to store the class diagram at uploads/<author>/
        class_storage_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', author)
        os.makedirs(class_storage_dir, exist_ok=True)

        # Create the new filename using the desired format
        doc_type = "class_diagram"
        new_file_name = f"{original_file_name}_{doc_type}_{doc_id}.png"
        final_output_path = os.path.join(class_storage_dir, new_file_name)

        # Move the generated diagram to the final location
        os.rename(class_output_path, final_output_path)

        # Open the generated diagram as a file
        with open(final_output_path, 'rb') as generated_file:
            # Store the class diagram in ClassDiagram model
            class_diagram = ClassDiagram.objects.create(
                language=language,
                author=author
            )
            class_diagram.file.save(os.path.basename(final_output_path), File(generated_file), save=True)  # Save the file to FileField

        # Return response with the path to the generated class diagram
        return Response({
            'message': 'Class diagram generated successfully',
            'class_diagram_path': final_output_path
        }, status=201)

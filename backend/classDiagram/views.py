from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ClassDiagram
from uploadMate.models import FileNest  # Import FileNest model to fetch uploaded code file
from django.conf import settings
from rest_framework import status
from django.core.files import File  # Import Django's File object
import os

# Import the class diagram generation utility function
from .utils import process_file

@api_view(['POST'])
def generate_class_diagram_view(request, doc_id):
    if not doc_id:
        return Response({'error': 'doc_id are required to fetch the uploaded files'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        file_nest = FileNest.objects.get(id=doc_id)
    except FileNest.DoesNotExist:
        return Response({'error': f'Uploaded file with id {doc_id} not found'}, status=status.HTTP_404_NOT_FOUND)

    uploaded_file_path = file_nest.file.path
    author = file_nest.author
    language = file_nest.language

    # Call process_file to handle generation and file management
    # class_diagram_Result returns file_path and file_name
    class_diagram_result = process_file(uploaded_file_path, language, author, doc_id)

    if class_diagram_result['file_path'] is None:
        return Response({'error': f'Class diagram generation failed for {doc_id}'}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

    # # Store the class diagram in the database
    # with open(class_diagram_path, 'rb') as generated_file:
    #     class_diagram = ClassDiagram.objects.create(
    #         language=language,
    #         author=author
    #     )
    #     class_diagram.file.save(os.path.basename(class_diagram_path), File(generated_file), save=True)

    # class_diagram_paths.append(class_diagram_path)

    file_name = class_diagram_result['file_name']
    file_url = f"{settings.MEDIA_URL}/{author}/{file_name}"

    return Response({
        'message': 'Class diagrams generated successfully',
        'file_url': file_url
    }, status=status.HTTP_201_CREATED)


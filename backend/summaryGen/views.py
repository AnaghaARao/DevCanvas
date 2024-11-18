from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import SummaryNest, SummaryEntry
from uploadMate.models import FileNest, FileEntry  # Import FileNest model to fetch uploaded code file
from django.conf import settings
from rest_framework import status
from django.core.files import File  # Import Django's File object
import os

from .utils import process_file


@api_view(['POST'])
def generate_summary_view(request, doc_id):
    # doc_ids = request.data.getlist('doc_ids')
    if not doc_id:
        return Response({'error': 'doc_id are required to fetch the uploaded files'}, status=status.HTTP_400_BAD_REQUEST)
    
    # summary_path = [] # for multiple files

    # for doc_id in doc_ids: # works for folder, file ent one by one
    try:
        file_nest = FileNest.objects.get(id=doc_id) # Get the directory-level record from FileNest
    except FileNest.DoesNotExist:
        return Response({'error': f'Uploaded directory with id {doc_id} not found'}, status=status.HTTP_404_NOT_FOUND)

    # Get all files in the directory associated with the given doc_id
    file_entries = FileEntry.objects.filter(file_nest=file_nest)
    
    if not file_entries.exists():
        return Response({'error': 'No files found in the specified directory'}, status=status.HTTP_404_NOT_FOUND)

    author = file_nest.author
    language = file_nest.language
    directory = file_nest.dir_name

    summary_result = process_file(directory, author)

    if 'error' in summary_result:
        return Response({'error':summary_result['error']}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

    # if summary_path is None:
    #     return Response({'error': f'Summary generation failed for {doc_id}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    summary_path = summary_result['summary_path'] # to get the path where summary pdf is stored

    if not isinstance(summary_path, str):
        return Response({'error': 'Summary path is not valid'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # # Store the class diagram in the database
    # with open(summary_path, 'rb') as generated_file:
    #     summary = SummaryDoc.objects.create(
    #         language=language,
    #         author=author
    #     )
    #     summary.file.save(os.path.basename(summary_path), File(generated_file), save=True)

    # summary_path.append(summary_path) # for multiple files

    # Return the file path or URL in the response
    file_name = summary_result['summary_file_name']
    file_url = f"{settings.MEDIA_URL}{author}/results/{file_name}"

    print('summary generated successfully')
    return Response({
        'message': 'Summary generated successfully',
        'file_url': file_url
    }, status=status.HTTP_201_CREATED)

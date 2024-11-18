from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from uploadMate.models import FileNest, FileEntry
from .models import FlowchartNest, FlowchartEntry
from uploadMate.models import FileNest, FileEntry  # Import FileNest model to fetch uploaded code file
from django.conf import settings
from rest_framework import status
from django.core.files import File  # Import Django's File object
import os

from .utils import process_file


@api_view(['POST'])
def generate_flowchart_view(request, doc_id):
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

    diagram_result = process_file(directory, author, language, doc_id)

    if diagram_result.get('error'):
        return diagram_result
    
    file_name = diagram_result['file_name']
    file_path = diagram_result['file_path']

    if not isinstance(file_path, str):
        return Response({'error': 'flowchart path is not valid'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    file_url = f"{settings.MEDIA_URL}{author}/results/{file_name}"

    return Response({
        'message':'flowchart generated successfully',
        'file_url': file_url
    }, status = status.HTTP_200_OK)
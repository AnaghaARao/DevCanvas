from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import SummaryDoc
from uploadMate.models import FileNest  # Import FileNest model to fetch uploaded code file
from django.conf import settings
from rest_framework import status
from django.core.files import File  # Import Django's File object
import os

from .utils import process_file


@api_view(['POST'])
def generate_class_diagram_view(request, doc_id):
    # doc_ids = request.data.getlist('doc_ids')
    if not doc_id:
        return Response({'error': 'doc_id are required to fetch the uploaded files'}, status=status.HTTP_400_BAD_REQUEST)
    
    # summary_path = [] # for multiple files

    # for doc_id in doc_ids: # works for folder, file ent one by one
    try:
        file_nest = FileNest.objects.get(id=doc_id)
    except FileNest.DoesNotExist:
        return Response({'error': f'Uploaded file with id {doc_id} not found'}, status=status.HTTP_404_NOT_FOUND)

    
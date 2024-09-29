from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import FileNest
from .serializers import DocumentUploadSerializer
from django.http import JsonResponse

# Create your views here.
@api_view(['POST'])
def upload_codebase(request):
    if request.method == 'POST':
        serializer = DocumentUploadSerializer(data=request.data)
        if serializer.is_valid():
            doc_upload = serializer.save()

            # check for file content type
            file = request.FILES['file']
            if file.content_type not in []:
                return Response({'error':'Unsupported file type'}, status=400)
            
            # send response based on docType
            if doc_upload.docType == 'summary':
                return Response({'redirect':'summary_app', 'doc_id':doc_upload.id}, status=201)
            elif doc_upload.docType == 'UML diagram':
                return Response({'redirect':'uml_app', 'doc_id':doc_upload.id}, status=201)
            else:
                return Response({'message':'Upload Successful, no specific route'}, status=201)
            
        return Response(serializer.errors, status=400)
            

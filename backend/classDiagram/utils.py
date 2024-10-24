import os
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from .java_class_diagram import JavaClassDiagramGenerator

def process_file(file_path, author, language, doc_id):
    if language == 'java':
        process = JavaClassDiagramGenerator(file_path, author, doc_id)
    elif language == 'pyton':
        pass
    else:
        return {'error':f"{language} not supported for class diagram generation"}
    
    analysis_result = process.analyze_java_file()

    if analysis_result['error']:
        return analysis_result
    
    classes = analysis_result
    
    png_result = process.generate_class_diagram(classes)

    if png_result['error']:
        return png_result
    
    img_path = png_result['img_path']
    media_url = settings.MEDIA_URL
    uploaded_file_name = os.path.splitext(os.path.basename(file_path))[0]
    file_name = f"class_diagram_{uploaded_file_name}.pdf"
    output_path = f"{media_url}{author}/{file_name}"
    pdf_result = process.generate_pdf(img_path, output_path, classes)

    if pdf_result['error']:
        return pdf_result
    
    return Response({
        'file_nme': file_name,
        'file_pth': output_path
    }, status = status.HTTP_200_OK)

import os
from django.conf import settings
from .java_class_diagram import JavaClassDiagramGenerator
from .python_class_diagram import PythonDiagramGenerator

def process_file(directory, author, language, doc_id):
    # Validate the language
    if language == 'java':
        process = JavaClassDiagramGenerator(directory, author, doc_id)
    elif language == 'python':  # Fix typo
        process = PythonDiagramGenerator(directory, author, doc_id)
    else:
        return {'error': f"{language} not supported for class diagram generation"}

    # Analyze the file
    analysis_result = process.analyze_directory()
    if analysis_result.get('error'):
        return analysis_result
    
    # Process the results
    classes = analysis_result

    # Generate the class diagram
    png_result = process.generate_class_diagram(classes)
    
    if png_result.get('error'):  # Check for errors in diagram generation
        return png_result

    # Prepare file paths and names
    img_path = png_result['img_path']
    media_root = settings.MEDIA_ROOT  # Use physical path for saving files
    # uploaded_file_name = os.path.splitext(os.path.basename(file_path))[0]
    file_name = f"class_diagram_{directory}.pdf"
    output_path = os.path.join(media_root, author, "results", file_name)  # Use media root for saving the file

    # Generate the PDF
    pdf_result = process.generate_pdf(img_path, output_path, classes)
    
    if pdf_result.get('error'):  # Check for errors in PDF generation
        return pdf_result
    
    # Return the success response with file name and path
    return {
        'file_name': file_name,
        'file_path': output_path
    }

import os
from django.conf import settings
from .java_class_diagram import JavaClassDiagramGenerator

def process_file(file_path, author, language, doc_id):
    # Validate the language
    if language == 'java':
        process = JavaClassDiagramGenerator(file_path, author, doc_id)
    elif language == 'python':  # Fix typo
        pass  # Add logic for python if needed
    else:
        return {'error': f"{language} not supported for class diagram generation"}

    # Analyze the Java file
    analysis_result = process.analyze_java_file()
    
    # Process the results
    classes = analysis_result

    # Generate the class diagram
    png_result = process.generate_class_diagram(classes)
    
    if png_result.get('error'):  # Check for errors in diagram generation
        return png_result

    # Prepare file paths and names
    img_path = png_result['img_path']
    media_root = settings.MEDIA_ROOT  # Use physical path for saving files
    uploaded_file_name = os.path.splitext(os.path.basename(file_path))[0]
    file_name = f"class_diagram_{uploaded_file_name}.pdf"
    output_path = os.path.join(media_root, author, file_name)  # Use media root for saving the file

    # Generate the PDF
    pdf_result = process.generate_pdf(img_path, output_path, classes)
    
    if pdf_result.get('error'):  # Check for errors in PDF generation
        return pdf_result
    
    # Return the success response with file name and path
    return {
        'file_name': file_name,
        'file_path': os.path.join(settings.MEDIA_URL, author, file_name)  # Return URL for access
    }

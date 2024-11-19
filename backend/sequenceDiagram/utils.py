import os
from django.conf import settings
from .python_sequence_diagram import MultiFileSequenceDiagramGenerator
from .java_sequence_diagram import JavaSequenceDiagramGenerator

def process_file(directory, author, language, doc_id):
    # Validate the language
    if language == 'python':
        process = MultiFileSequenceDiagramGenerator(directory, author, doc_id)
    elif language == 'java':
        process = JavaSequenceDiagramGenerator(directory, author, doc_id)
    else:
        return {'error': f"{language} not supported for class diagram generation"}

    # Analyze the file
    analysis_result = process.analyze_directory()
    if analysis_result['status'] == 'error':
        return analysis_result
    
    output_dir = os.path.join(settings.MEDIA_ROOT, author, "results")
    os.makedirs(output_dir, exist_ok=True)

    file_name = f"summary_{directory}.pdf"
    output_path = os.path.join(output_dir, file_name)

    # Generate the PDF
    pdf_result = process.generate_pdf(output_path)
    
    if pdf_result['status']=='error':  # Check for errors in PDF generation
        return pdf_result
    else:
    # Return the success response with file name and path
        return {
            'file_name': file_name,
            'file_path': output_path
        }

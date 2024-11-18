import os
from django.conf import settings
from .python_sequence_diagram import MultiFileSequenceDiagramGenerator

def process_file(directory, author, language, doc_id):
    # Validate the language
    if language == 'python':
        process = MultiFileSequenceDiagramGenerator(directory, author, doc_id)
    else:
        return {'error': f"{language} not supported for class diagram generation"}

    # Analyze the file
    analysis_result = process.analyze_directory()
    if analysis_result['status'] == 'error':
        return analysis_result['error']
    

    
    # # Process the results
    # classes = analysis_result

    # # Generate the class diagram
    # png_result = process.generate_sequence_diagram(classes)
    
    # if png_result.get('error'):  # Check for errors in diagram generation
    #     return png_result

    # Prepare file paths and names
    # img_path = png_result['img_path']
    # media_root = settings.MEDIA_ROOT  # Use physical path for saving files
    # uploaded_file_name = os.path.splitext(os.path.basename(file_path))[0]
    file_name = f"sequence_diagram_{directory}.pdf"
    output_path = os.path.join(settings.MEDIA_ROOT, author, directory, file_name)

    # Generate the PDF
    pdf_result = process.generate_pdf(output_path)
    
    if pdf_result['status']=='error':  # Check for errors in PDF generation
        return pdf_result['error']
    else:
    # Return the success response with file name and path
        return {
            'file_name': file_name,
            'file_path': output_path
        }

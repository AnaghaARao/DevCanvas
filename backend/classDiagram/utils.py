import os
from .class_diagram_generator import JavaDiagramGenerator, PythonDiagramGenerator

def process_file(file_path, language, author, doc_id):
    # Select the appropriate diagram generator class based on the language
    if language == 'java':
        processor = JavaDiagramGenerator(file_path, author, doc_id)
    elif language == 'python':
        processor = PythonDiagramGenerator(file_path, author, doc_id)
    else:
        return {'error': f'Unsupported language: {language}'}
    
    # Analyze the file (common for both Java and Python)
    result = processor.analyze_file()

    # If there's an error in file analysis, return the error
    if 'error' in result:
        return {
            'error': result[0]['error'],
            'details': result[0]['details']
        }

    # Proceed with class diagram generation if no errors
    classes = result  # Only classes are relevant, the second value is ignored

    # Generate and save the class diagram as a PDF
    class_diagram_file_path, class_diagram_file_name = processor.save_diagrams(classes, file_path)

    # Prepare the response to be sent to the frontend
    response = {
        'file_path': class_diagram_file_path,
        'file_name': class_diagram_file_name
    }

    return response

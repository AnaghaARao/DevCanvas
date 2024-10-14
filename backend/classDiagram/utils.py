import os
from .class_diagram_generator import JavaDiagramGenerator, JavaScriptDiagramGenerator

def process_file(file_path, language, author, doc_id):
    if language == 'java':
        processor = JavaDiagramGenerator(file_path, author, doc_id)
    elif language == 'javascript':
        processor = JavaScriptDiagramGenerator(file_path, author, doc_id)
    else:
        return {'error':f'Unsupported language: {language}'}
    
    result = processor.analyze_file()

    if 'error' in result[0]:
        # Return error message to be passed to the frontend
        return {
            'error': result[0]['error'],
            'details': result[0]['details']
        }

    # Proceed with diagram generation if no errors
    classes, methods = result

    # Call diagram generation methods as usual
    class_diagram_path, flowchart_paths = processor.save_diagrams(classes, methods)
    
    return {
        'class_diagram': class_diagram_path,
        'flowcharts': flowchart_paths
    }

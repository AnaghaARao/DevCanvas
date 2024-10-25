import ast
import pydot
import os
import sys
import logging
import multiprocessing
from typing import Dict, List, Tuple
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from django.conf import settings

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ClassInfo:
    def __init__(self, name: str):
        self.name = name
        self.methods: List[str] = []
        self.attributes: List[str] = []
        self.base_classes: List[str] = []
        self.compositions: List[Tuple[str, str]] = []  # (attribute_name, class_name)

    def __str__(self):
        return f"ClassInfo(name={self.name}, methods={self.methods}, attributes={self.attributes}, base_classes={self.base_classes}, compositions={self.compositions})"
    
class PythonDiagramGenerator:
    def __init__(self, file_path, author, doc_id):
        self.file_path = file_path
        self.author = author
        self.doc_id = doc_id

    def analyze_file(self):
        classes = {}
        uploaded_file_path = self.file_path
        with open(uploaded_file_path, 'r') as file:
            try:
                tree = ast.parse(file.read(), filename=uploaded_file_path)
            except SyntaxError as e:
                logging.error(f"Syntax error in {uploaded_file_path}: {e}")
                return {'error':f'syntax error in {uploaded_file_path}: {e}'}

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    class_info = ClassInfo(class_name)
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info.methods.append(item.name)
                        elif isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    class_info.attributes.append(target.id)
                    
                    # Handle base classes
                    class_info.base_classes = [
                        base.id if isinstance(base, ast.Name) else ast.unparse(base) 
                        for base in node.bases
                    ]
                    
                    # Detect composition relationships
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name) and isinstance(item.value, ast.Call):
                                    if isinstance(item.value.func, ast.Name):
                                        class_info.compositions.append((target.id, item.value.func.id))
                    
                    classes[class_name] = class_info

        return classes
    
    def generate_class_diagram(self, classes):
        graph = pydot.Dot(graph_type='digraph')
        graph.set_rankdir('TB')
        graph.set_size('8.5,11')  # Set size to letter paper dimensions
        graph.set_dpi('300')  # Increase DPI for better quality

        if not classes:
            logging.warning("No classes found to generate diagram.")
            return graph

        for class_name, class_info in classes.items():
            label = f'{{{class_name}|'
            if class_info.attributes:
                label += '\\n'.join(class_info.attributes) + '|'
            label += '\\n'.join(class_info.methods) + '}'
            
            node = pydot.Node(class_name, label=label, shape='record')
            graph.add_node(node)

            for base_class in class_info.base_classes:
                if base_class in classes:
                    edge = pydot.Edge(base_class, class_name, label='inherits')
                    graph.add_edge(edge)

            for attr, comp_class in class_info.compositions:
                if comp_class in classes:
                    edge = pydot.Edge(class_name, comp_class, label=f'has {attr}', style='dashed')
                    graph.add_edge(edge)

        uploaded_file_name = os.path.splitext(os.path.basename(self.file_path))[0]
        file_name = f"class_diagram_{uploaded_file_name}"
        result = self.safe_write_png(graph, file_name)
        return result
    
    def safe_write_png(self, graph, filename):
        output_path = os.path.join(settings.MEDIA_URL, filename)
        try:
            graph.write_png(output_path)
            logging.info(f"Generated: {output_path}")
            return {'img_path':output_path}
        except Exception as e:
            logging.error(f"Error writing {filename}: {str(e)}")
            logging.error(f"Make sure you have write permissions in {settings.MEDIA_URL}")
            return {'error':f'Error writing {filename}: {str(e)}'}

    def generate_pdf(self, diagram_path: str, output_path: str, classes: Dict[str, ClassInfo]):
        try:
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Add title
            title = Paragraph("Python Class Diagram", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))

            # Add description
            description = Paragraph("This is a UML class diagram representing the structure of the analyzed Python code. "
                                    "It shows classes, their attributes, methods, and relationships.", styles['Normal'])
            story.append(description)
            story.append(Spacer(1, 12))

            # Add the diagram image
            img = Image(diagram_path, width=500, height=500)
            story.append(img)
            story.append(Spacer(1, 12))

            # Add class information
            for class_name, class_info in classes.items():
                class_title = Paragraph(f"Class: {class_name}", styles['Heading2'])
                story.append(class_title)
                
                if class_info.attributes:
                    attributes = Paragraph(f"Attributes: {', '.join(class_info.attributes)}", styles['Normal'])
                    story.append(attributes)
                
                if class_info.methods:
                    methods = Paragraph(f"Methods: {', '.join(class_info.methods)}", styles['Normal'])
                    story.append(methods)
                
                if class_info.base_classes:
                    base_classes = Paragraph(f"Base Classes: {', '.join(class_info.base_classes)}", styles['Normal'])
                    story.append(base_classes)
                
                if class_info.compositions:
                    compositions = Paragraph(f"Compositions: {', '.join([f'{attr} ({comp_class})' for attr, comp_class in class_info.compositions])}", styles['Normal'])
                    story.append(compositions)
                
                story.append(Spacer(1, 12))

            doc.build(story)
            return {'message':'pdf successfully generated'}
        except Exception as e:
            return {'error':'error in generating pdf'}
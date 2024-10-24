import os
import sys
import javalang
import pydot
import logging
import multiprocessing
from typing import Dict, List, Tuple
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from django.conf import settings

media_url = settings.MEDIA_URL

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ClassInfo:
    def __init__(self, name: str):
        self.name = name
        self.methods: List[str] = []
        self.attributes: List[str] = []
        self.base_class: str = None
        self.interfaces: List[str] = []

    def __str__(self):
        return f"ClassInfo(name={self.name}, methods={self.methods}, attributes={self.attributes}, base_class={self.base_class}, interfaces={self.interfaces})"
    
class JavaClassDiagramGenerator:
    def __init__(self, file_path, author, doc_id):
        self.file_path = file_path
        self.author = author
        self.doc_id = doc_id

    def analyze_java_file(self):
        uploaded_file_path = self.file_path
        classes = {}
        with open(uploaded_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        try:
            tree = javalang.parse.parse(content)
        except javalang.parser.JavaSyntaxError:
            logging.error(f"Syntax error in file: {uploaded_file_path}")
            return {}

        for path, node in tree.filter(javalang.tree.ClassDeclaration):
            class_name = node.name
            class_info = ClassInfo(class_name)
            
            class_info.methods = [m.name for m in node.methods]
            class_info.base_class = node.extends.name if node.extends else None
            class_info.interfaces = [i.name for i in node.implements] if node.implements else []
            
            for field in node.fields:
                for declarator in field.declarators:
                    class_info.attributes.append(f"{field.type.name} {declarator.name}")
            
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

            if class_info.base_class:
                edge = pydot.Edge(class_info.base_class, class_name, label='extends')
                graph.add_edge(edge)

            for interface in class_info.interfaces:
                edge = pydot.Edge(interface, class_name, label='implements', style='dashed')
                graph.add_edge(edge)

        uploaded_file_name = os.path.splitext(os.path.basename(self.file_path))[0]

        file_name = f"class_diagram_{uploaded_file_name}"
        self.safe_write_png(graph, file_name)

    def safe_write_png(self, graph, filename):
        output_path = os.path.join(media_url, filename)
        try:
            graph.write_png(output_path)
            logging.info(f"Generated: {output_path}")
            return {'img_path':output_path}
        except Exception as e:
            logging.error(f"Error writing {filename}: {str(e)}")
            logging.error(f"Make sure you have write permissions in {media_url}") 
            return {'error':f'Error writing {filename}: {str(e)}'}
        

    def generate_pdf(self, diagram_path: str, output_path: str, classes: Dict[str, ClassInfo]):
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add title
        title = Paragraph("Java Class Diagram", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))

        # Add description
        description = Paragraph("This is a UML class diagram representing the structure of the analyzed Java code. "
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
            
            if class_info.base_class:
                base_class = Paragraph(f"Base Class: {class_info.base_class}", styles['Normal'])
                story.append(base_class)
            
            if class_info.interfaces:
                interfaces = Paragraph(f"Interfaces: {', '.join(class_info.interfaces)}", styles['Normal'])
                story.append(interfaces)
            
            story.append(Spacer(1, 12))

        doc.build(story)
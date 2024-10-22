import os
import ast
import pydot
import logging
import javalang
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from multiprocessing import Pool
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from typing import Dict, List, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Common Class to Hold Class Information
class ClassInfo:
    def __init__(self, name: str):
        self.name = name
        self.methods = []
        self.attributes = []
        self.base_classes = []

    def __str__(self):
        return f"ClassInfo(name={self.name}, methods={self.methods}, attributes={self.attributes}, base_classes={self.base_classes})"


# Python Diagram Generator
class PythonDiagramGenerator:
    def __init__(self, file_path, author, doc_id):
        self.file_path = file_path
        self.author = author
        self.doc_id = doc_id
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.classes = {}

    def analyze_file(self, file_path: str) -> Dict[str, ClassInfo]:
        classes = {}
        with open(file_path, 'r') as file:
            try:
                tree = ast.parse(file.read(), filename=file_path)
            except SyntaxError as e:
                logging.error(f"Syntax error in {file_path}: {e}")
                return {}

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

    def analyze_directory(self) -> Dict[str, ClassInfo]:
        all_classes = {}
        file_paths = [self.file_path]  # Only analyzing the single file path

        with Pool() as pool:
            results = pool.map(self.analyze_file, file_paths)
            for result in results:
                all_classes.update(result)
        
        if not all_classes:
            logging.error(f"No classes found in the file: {self.file_path}")
        else:
            logging.info(f"Found {len(all_classes)} classes in the file: {self.file_path}")
        
        return all_classes

    def generate_class_diagram(self, classes: Dict[str, ClassInfo]) -> pydot.Dot:
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

        return graph

    def save_diagrams(self, classes, file_path):
        class_dia_dir = os.path.dirname(file_path)
        # summary_file_name = f"summary_{os.path.basename(file_path)}.pdf"
        # Get the base filename without the extension
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        class_dia_file_name = f"class_diagram_{base_name}.png"
        class_dia_file_path = os.path.join(class_dia_dir, class_dia_file_name)
        # Save the summary to the PDF file
        self.generate_class_diagram(classes)
        return class_dia_file_path, class_dia_file_name

    def analyze_file_and_generate_diagram(self):
        # Analyze the Python file and generate class diagram
        logging.info(f"Processing file: {self.file_path}")
        classes = self.analyze_directory()

        if not classes:
            return [{'error': 'No classes found in the file.', 'details': 'Please check the file content.'}], None

        return classes, list(classes.keys())



# Java Diagram Generator
class JavaDiagramGenerator:
    def __init__(self, file_path, author, doc_id):
        self.file_path = file_path
        self.author = author
        self.doc_id = doc_id

    def analyze_file(self):
        """Parses the Java file and extracts class information."""
        logging.info(f"Analyzing Java file: {self.file_path}")
        classes = {}
        try:
            with open(self.file_path, 'r') as file:
                tree = javalang.parse.parse(file.read())
        except Exception as e:
            logging.error(f"Error reading or parsing Java file {self.file_path}: {e}")
            return [{'error': 'File Parsing Error', 'details': str(e)}], []

        for path, node in tree.filter(javalang.tree.ClassDeclaration):
            class_info = ClassInfo(node.name)
            for member in node.body:
                if isinstance(member, javalang.tree.MethodDeclaration):
                    class_info.methods.append(member.name)
                elif isinstance(member, javalang.tree.FieldDeclaration):
                    for declarator in member.declarators:
                        class_info.attributes.append(declarator.name)
            if node.extends:
                class_info.base_classes.append(node.extends.name)
            classes[node.name] = class_info

        if not classes:
            logging.warning(f"No classes found in {self.file_path}.")
            return [{'error': 'No classes found', 'details': 'No class definitions were detected in the provided file.'}], []
        
        logging.info(f"Classes found in Java: {list(classes.keys())}")
        return classes

    def save_diagrams(self, classes, file_path):
        class_dia_dir = os.path.dirname(file_path)
        # summary_file_name = f"summary_{os.path.basename(file_path)}.pdf"
        # Get the base filename without the extension
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        class_dia_file_name = f"class_diagram_{base_name}.pdf"
        class_dia_file_path = os.path.join(class_dia_dir, class_dia_file_name)
        # Save the summary to the PDF file
        self.generate_pdf(classes, class_dia_file_path)
        return class_dia_file_path, class_dia_file_name


    # def save_diagrams(self, classes):
    #     # Specify the author directory
    #     author_dir = os.path.join('uploads', self.author)  # This is correct
        
    #     # Ensure the directory exists
    #     if not os.path.exists(author_dir):
    #         os.makedirs(author_dir)

    #     # Construct the file name
    #     file_name = f'class_diagram_{self.doc_id}.pdf'
        
    #     # Correct file path construction
    #     file_path = os.path.join(author_dir, file_name)

    #     return file_path, file_name
    
        # author_dir = os.path.join('uploads', self.author)
        
        # # Ensure the directory exists
        # if not os.path.exists(author_dir):
        #     os.makedirs(author_dir)

        # # Construct the file name
        # file_name = f'class_diagram_{self.doc_id}.pdf'
        # file_path = os.path.join(author_dir, file_name)

        # return file_path, file_name
    
        # """Generates a PDF with class information and saves it."""
        # original_file_name = os.path.basename(self.file_path).replace('.java', '')  # Extract the file name without extension
        # output_dir = os.path.join('path_to_store_files', self.author)  # Replace with actual path
        # if not os.path.exists(output_dir):
        #     os.makedirs(output_dir)
        #     logging.info(f"Created directory: {output_dir}")
        
        # pdf_file_name = f"class_diagram_{original_file_name}.pdf"
        # pdf_path = os.path.join(output_dir, pdf_file_name)

        # logging.info(f"Saving Java class diagram as PDF: {pdf_file_name} in {output_dir}")
        # self.generate_pdf(classes, pdf_path)

        # return pdf_path, pdf_file_name

    def generate_pdf(self, classes, output_path):
        """Generates a PDF file with the class diagram details."""
        logging.info(f"Generating PDF report for Java classes at {output_path}")
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add title
        title = Paragraph("Java Class Diagram", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))

        # Add description
        description = Paragraph("This is a UML class diagram representing the structure of the analyzed Java code. "
                                "It shows classes, their attributes, methods, and base classes.", styles['Normal'])
        story.append(description)
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
            
            story.append(Spacer(1, 12))

        doc.build(story)
        logging.info(f"PDF generation complete at: {output_path}")
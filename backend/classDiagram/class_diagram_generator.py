import os
import ast
import logging
import javalang
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet




# Python Diagram Generator
class PythonDiagramGenerator:
    def __init__(self, file_path, author, doc_id):
        self.file_path = file_path
        self.author = author
        self.doc_id = doc_id

    def analyze_file(self):
        """Parses the Python file and extracts class information."""
        logging.info(f"Analyzing Python file: {self.file_path}")
        classes = {}
        try:
            with open(self.file_path, 'r') as file:
                tree = ast.parse(file.read(), filename=self.file_path)
        except Exception as e:
            logging.error(f"Error reading or parsing Python file {self.file_path}: {e}")
            return [{'error': 'File Parsing Error', 'details': str(e)}], []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = ClassInfo(node.name)
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        class_info.methods.append(item.name)
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                class_info.attributes.append(target.id)
                class_info.base_classes = [
                    base.id if isinstance(base, ast.Name) else ast.unparse(base)
                    for base in node.bases
                ]
                classes[node.name] = class_info

        if not classes:
            logging.warning(f"No classes found in {self.file_path}.")
            return [{'error': 'No classes found', 'details': 'No class definitions were detected in the provided file.'}], []
        
        logging.info(f"Classes found in Python: {list(classes.keys())}")
        return classes, []

    def save_diagrams(self, classes):
        """Generates a PDF with class information and saves it."""
        original_file_name = os.path.basename(self.file_path).replace('.py', '')  # Extract the file name without extension
        output_dir = os.path.join('path_to_store_files', self.author)  # Replace with actual path
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logging.info(f"Created directory: {output_dir}")
        
        pdf_file_name = f"class_diagram_{original_file_name}.pdf"
        pdf_path = os.path.join(output_dir, pdf_file_name)

        logging.info(f"Saving Python class diagram as PDF: {pdf_file_name} in {output_dir}")
        self.generate_pdf(classes, pdf_path)

        return pdf_path, pdf_file_name

    def generate_pdf(self, classes, output_path):
        """Generates a PDF file with the class diagram details."""
        logging.info(f"Generating PDF report for Python classes at {output_path}")
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add title
        title = Paragraph("Python Class Diagram", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))

        # Add description
        description = Paragraph("This is a UML class diagram representing the structure of the analyzed Python code. "
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
import ast
import pydot
import os
import sys
import logging
import multiprocessing
from typing import Dict, List, Tuple
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether, Frame, PageTemplate
from reportlab.lib import colors
from datetime import datetime
from reportlab.lib.utils import ImageReader
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
    def __init__(self, directory, author, doc_id):
        self.directory = f"{settings.MEDIA_ROOT}/{author}/{directory}"
        self.author = author
        self.doc_id = doc_id
        self.dir_name = directory

    def analyze_file(self, file_path):
        classes = {}
        # uploaded_file_path = self.file_path
        with open(file_path, 'r') as file:
            try:
                tree = ast.parse(file.read(), filename=file_path)
            except SyntaxError as e:
                logging.error(f"Syntax error in {file_path}: {e}")
                return {'error':f'syntax error in {file_path}: {e}'}

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
    
    def list_python_files(self) -> List[str]:
        python_files = []
        logging.info(f"Checking files in directory: {self.directory}")
        for root, _, files in os.walk(self.directory):
            for file in files:
                full_path = os.path.join(root, file)
                logging.info(f"Found file: {full_path}")
                if file.endswith('.py'):
                    python_files.append(full_path)
                    logging.info(f"Identified Python file: {full_path}")
        return python_files

    def analyze_directory(self) -> Dict[str, ClassInfo]:
        all_classes = {}
        file_paths = self.list_python_files()
        
        if not file_paths:
            logging.error(f"No Python files found in directory: {self.directory}")
            return all_classes

        with multiprocessing.Pool() as pool:
            results = pool.map(self.analyze_file, file_paths)
            for result in results:
                all_classes.update(result)
        
        if not all_classes:
            logging.error(f"No classes found in any of the {len(file_paths)} Python files analyzed.")
        else:
            logging.info(f"Found {len(all_classes)} classes in {len(file_paths)} Python files.")
        
        return all_classes
    
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

        # uploaded_file_name = os.path.splitext(os.path.basename(self.file_path))[0]
        file_name = f"class_diagram_{self.dir_name}"
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
        
    def create_header_footer(self, canvas, doc):
        """Create a minimalist header and footer with separating lines"""
        canvas.saveState()
        
        # Header positioning
        header_top = doc.pagesize[1] - 40
        
        # Add logo
        logo_path = settings.MEDIA_LOGO
        if os.path.exists(logo_path):
        
            img = ImageReader(logo_path)
            canvas.drawImage(logo_path, 
                            doc.leftMargin - 20,
                            header_top - 35,
                            width=40, 
                            height=40,
                            preserveAspectRatio=True)
        
        # Add DevCanvas text next to logo
        canvas.setFont('Helvetica-Bold', 14)
        canvas.setFillColor(colors.Color(0.2, 0.2, 0.2))
        canvas.drawString(doc.leftMargin + 30, 
                        header_top - 25,
                        "DevCanvas")
        
        # Add report generation date
        canvas.setFont('Helvetica', 10)
        canvas.setFillColor(colors.Color(0.4, 0.4, 0.4))
        date_str = datetime.now().strftime('%B %d, %Y')
        canvas.drawString(doc.width + doc.leftMargin - 120,
                        header_top - 25,
                        f"Generated: {date_str}")
        
        # Header separation line
        canvas.setStrokeColor(colors.Color(0.8, 0.8, 0.8))
        canvas.line(doc.leftMargin - 30,
                    header_top - 45,
                    doc.width + doc.leftMargin + 30,
                    header_top - 45)
        
        # Footer separation line
        canvas.line(doc.leftMargin - 30,
                    doc.bottomMargin - 20,
                    doc.width + doc.leftMargin + 30,
                    doc.bottomMargin - 20)
        
        # Footer text
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.Color(0.4, 0.4, 0.4))
        canvas.drawString(doc.leftMargin, 
                        doc.bottomMargin - 35,
                        " © Generated by DevCanvas")
        
        # Add page number
        page_num = canvas.getPageNumber()
        canvas.drawRightString(doc.width + doc.leftMargin,
                            doc.bottomMargin - 35,
                            f"Page {page_num}")
        
        canvas.restoreState()

    def generate_pdf(self, diagram_path: str, output_path: str, classes: Dict[str, ClassInfo]):
        try:
            """Generate a comprehensive PDF report with class diagram and detailed analysis."""
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=110,  # Adjusted for header
                bottomMargin=72
            )
            
            # Create custom styles
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(
                name='CustomHeading1',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=20,
                textColor=colors.Color(0.2, 0.2, 0.2)
            ))
            styles.add(ParagraphStyle(
                name='CustomHeading2',
                parent=styles['Heading2'],
                fontSize=16,
                spaceBefore=15,
                spaceAfter=10,
                textColor=colors.Color(0.3, 0.3, 0.3)
            ))
            styles.add(ParagraphStyle(
                name='CustomBody',
                parent=styles['Normal'],
                fontSize=11,
                leading=14,
                spaceBefore=6,
                spaceAfter=6,
                textColor=colors.Color(0.3, 0.3, 0.3)
            ))
            
            story = []
            
            # Title
            title = Paragraph("Python Class Diagram Analysis Report", styles['CustomHeading1'])
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Executive Summary
            story.append(Paragraph("Executive Summary", styles['CustomHeading2']))
            summary_text = Paragraph(
                f"This report presents a comprehensive analysis of the Python codebase structure "
                f"through class diagrams and detailed documentation. The analysis covers {len(classes)} "
                f"classes and their relationships.",
                styles['CustomBody']
            )
            story.append(summary_text)
            story.append(Spacer(1, 20))
            
            # Class Diagram Section
            story.append(Paragraph("Class Diagram", styles['CustomHeading2']))
            diagram_intro = Paragraph(
                "The following UML class diagram illustrates the relationships between classes "
                "in the codebase using standard UML notation.",
                styles['CustomBody']
            )
            story.append(diagram_intro)
            story.append(Spacer(1, 10))
            
            # Add diagram with KeepTogether to prevent awkward breaks
            diagram_elements = [
                Image(diagram_path, width=7*inch, height=7*inch),
                Spacer(1, 10),
                Paragraph("Figure 1: UML Class Diagram", styles['CustomBody'])
            ]
            story.append(KeepTogether(diagram_elements))
            story.append(PageBreak())
            
            # Detailed Class Analysis
            story.append(Paragraph("Detailed Class Analysis", styles['CustomHeading2']))
            
            for class_name, class_info in classes.items():
                # Create a list of elements for each class analysis
                class_elements = []
                class_elements.append(Paragraph(f"Class: {class_name}", styles['CustomHeading2']))
                
                # Create class details table
                data = [
                    ["Attributes", "Methods", "Base Classes", "Compositions"],
                    [
                        "\n".join(class_info.attributes) if class_info.attributes else "None",
                        "\n".join(class_info.methods) if class_info.methods else "None",
                        "\n".join(class_info.base_classes) if class_info.base_classes else "None",
                        "\n".join([f"{attr} ({cls})" for attr, cls in class_info.compositions]) if class_info.compositions else "None"
                    ]
                ]
                
                table = Table(data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 1, colors.Color(0.8, 0.8, 0.8)),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.95, 0.95, 0.95)),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.Color(0.3, 0.3, 0.3)),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('PADDING', (0, 0), (-1, -1), 6),
                ]))
                
                class_elements.append(table)
                class_elements.append(Spacer(1, 15))
                
                # Keep all elements of a single class analysis together
                story.append(KeepTogether(class_elements))
            
            # Metrics Section
            story.append(PageBreak())
            story.append(Paragraph("Metrics and Statistics", styles['CustomHeading2']))
            
            metrics_data = [
                ['Metric', 'Value'],
                ['Total Classes', str(len(classes))],
                ['Average Methods per Class', f"{sum(len(c.methods) for c in classes.values()) / len(classes):.1f}"],
                ['Average Attributes per Class', f"{sum(len(c.attributes) for c in classes.values()) / len(classes):.1f}"],
                ['Classes with Inheritance', str(sum(1 for c in classes.values() if c.base_classes))],
                ['Classes with Compositions', str(sum(1 for c in classes.values() if c.compositions))]
            ]
            
            metrics_table = Table(metrics_data, colWidths=[3*inch, 3*inch])
            metrics_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.Color(0.8, 0.8, 0.8)),
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.95, 0.95, 0.95)),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.Color(0.3, 0.3, 0.3)),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('PADDING', (0, 0), (-1, -1), 12),
            ]))
            
            story.append(metrics_table)

            # Build the PDF
            doc.build(story, onFirstPage=self.create_header_footer, onLaterPages=self.create_header_footer)
            return {'message':'pdf successfully generated'}
        except Exception as e:
            return {'error':'error in generating pdf'}
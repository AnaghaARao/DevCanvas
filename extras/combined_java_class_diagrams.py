import os
import sys
import javalang
import pydot
import logging
import multiprocessing
from typing import Dict, List, Tuple
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime

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

# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Move one directory up and then set the input directory path to 'testing/java'
project_root = os.path.dirname(current_dir)
input_dir = os.path.join(project_root, 'testing', 'java')

logging.info(f"Set input directory to: {input_dir}")

def safe_write_png(graph, filename):
    output_path = os.path.join(current_dir, filename)
    try:
        graph.write_png(output_path)
        logging.info(f"Generated: {output_path}")
    except Exception as e:
        logging.error(f"Error writing {filename}: {str(e)}")
        logging.error(f"Make sure you have write permissions in {current_dir}")

def analyze_java_file(file_path: str) -> Dict[str, ClassInfo]:
    classes = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    try:
        tree = javalang.parse.parse(content)
    except javalang.parser.JavaSyntaxError:
        logging.error(f"Syntax error in file: {file_path}")
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

def list_java_files(directory: str) -> List[str]:
    java_files = []
    logging.info(f"Checking files in directory: {directory}")
    for root, _, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            logging.info(f"Found file: {full_path}")
            if file.endswith('.java'):
                java_files.append(full_path)
                logging.info(f"Identified Java file: {full_path}")
    return java_files

def analyze_directory(directory: str) -> Dict[str, ClassInfo]:
    all_classes = {}
    file_paths = list_java_files(directory)
    
    if not file_paths:
        logging.error(f"No Java files found in directory: {directory}")
        return all_classes

    with multiprocessing.Pool() as pool:
        results = pool.map(analyze_java_file, file_paths)
        for result in results:
            all_classes.update(result)
    
    if not all_classes:
        logging.error(f"No classes found in any of the {len(file_paths)} Java files analyzed.")
    else:
        logging.info(f"Found {len(all_classes)} classes in {len(file_paths)} Java files.")
    
    return all_classes

def generate_class_diagram(classes: Dict[str, ClassInfo]) -> pydot.Dot:
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

    return graph

def generate_enhanced_pdf(diagram_path: str, output_path: str, classes: Dict[str, ClassInfo], is_java: bool = True):
    """
    Generate a continuous PDF report with class diagram and detailed analysis.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Create custom styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CustomHeading1',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    ))
    styles.add(ParagraphStyle(
        name='CustomHeading2',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        spaceBefore=8,
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name='Caption',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        alignment=1
    ))
    
    story = []
    
    # Title and Executive Summary
    title = Paragraph("Java Class Diagram Analysis Report", styles['CustomHeading1'])
    date = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", styles['CustomBody'])
    
    story.extend([
        title,
        Spacer(1, 20),
        date,
        Spacer(1, 30),
        Paragraph("Executive Summary", styles['CustomHeading2']),
        Paragraph(
            f"This report presents a comprehensive analysis of the Java codebase structure "
            f"through class diagrams and detailed documentation. The analysis covers {len(classes)} "
            f"classes and their relationships, providing insights into the system's architecture "
            "and design patterns.",
            styles['CustomBody']
        ),
        Spacer(1, 20)
    ])
    
    # Table of Contents
    story.extend([
        Paragraph("Table of Contents", styles['CustomHeading2']),
        Paragraph("1. Introduction", styles['CustomBody']),
        Paragraph("2. Class Diagram", styles['CustomBody']),
        Paragraph("3. Detailed Class Analysis", styles['CustomBody']),
        Paragraph("4. Relationships and Dependencies", styles['CustomBody']),
        Paragraph("5. Metrics and Statistics", styles['CustomBody']),
        Spacer(1, 20)
    ])
    
    # Introduction
    story.extend([
        Paragraph("1. Introduction", styles['CustomHeading2']),
        Paragraph(
            "This report analyzes the structure and relationships of Java classes in the "
            "codebase. The analysis includes class hierarchies, relationships, methods, and attributes. "
            "The visualization is presented through a UML class diagram, followed by detailed "
            "documentation of each component.",
            styles['CustomBody']
        ),
        Spacer(1, 20)
    ])
    
    # Class Diagram Section
    story.extend([
        Paragraph("2. Class Diagram", styles['CustomHeading2']),
        Paragraph(
            "The following UML class diagram illustrates the relationships between classes "
            "in the codebase. The diagram uses standard UML notation:",
            styles['CustomBody']
        ),
        Paragraph(
            "• Solid lines with arrows indicate inheritance relationships<br/>"
            "• Dashed lines indicate implementation relationships<br/>"
            "• Boxes show class names, attributes, and methods",
            styles['CustomBody']
        ),
        Spacer(1, 20),
        Image(diagram_path, width=7*inch, height=7*inch),
        Paragraph("Figure 1: UML Class Diagram", styles['Caption']),
        Spacer(1, 20)
    ])
    
    # Detailed Class Analysis
    story.extend([
        Paragraph("3. Detailed Class Analysis", styles['CustomHeading2']),
        Paragraph(
            "This section provides a detailed analysis of each class in the system, "
            "including their responsibilities, relationships, and components.",
            styles['CustomBody']
        )
    ])
    
    for class_name, class_info in classes.items():
        story.extend([
            Paragraph(f"Class: {class_name}", styles['CustomHeading2']),
            Paragraph("Description:", styles['CustomBody'])
        ])
        
        data = [
            ["Attributes", "Methods", "Base Class", "Interfaces"],
            [
                "\n".join(class_info.attributes) if class_info.attributes else "None",
                "\n".join(class_info.methods) if class_info.methods else "None",
                class_info.base_class if class_info.base_class else "None",
                "\n".join(class_info.interfaces) if class_info.interfaces else "None"
            ]
        ]
        
        table = Table(data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ]))
        
        story.extend([
            table,
            Spacer(1, 20)
        ])
    
    # Relationships and Dependencies
    story.extend([
        Paragraph("4. Relationships and Dependencies", styles['CustomHeading2']),
        Paragraph(
            "This section outlines the key relationships and dependencies between classes:",
            styles['CustomBody']
        )
    ])
    
    for class_name, class_info in classes.items():
        relationships = []
        if class_info.base_class:
            relationships.append(f"• Inherits from {class_info.base_class}")
        if class_info.interfaces:
            relationships.append(f"• Implements interfaces: {', '.join(class_info.interfaces)}")
        
        if relationships:
            story.extend([
                Paragraph(f"{class_name} Relationships:", styles['CustomBody']),
                Paragraph("<br/>".join(relationships), styles['CustomBody']),
                Spacer(1, 10)
            ])
    
    # Metrics and Statistics
    story.extend([
        Paragraph("5. Metrics and Statistics", styles['CustomHeading2']),
        Paragraph(
            f"Summary of codebase metrics:<br/>"
            f"• Total number of classes: {len(classes)}<br/>"
            f"• Average methods per class: {sum(len(c.methods) for c in classes.values()) / len(classes):.1f}<br/>"
            f"• Average attributes per class: {sum(len(c.attributes) for c in classes.values()) / len(classes):.1f}<br/>"
            f"• Classes with inheritance: {sum(1 for c in classes.values() if c.base_class)}<br/>"
            f"• Classes with interfaces: {sum(1 for c in classes.values() if c.interfaces)}",
            styles['CustomBody']
        )
    ])
    
    # Build the PDF
    doc.build(story)

def main():
    logging.info(f"Analyzing directory: {input_dir}")
    classes = analyze_directory(input_dir)
    
    if not classes:
        logging.error("No classes found in the specified directory. Please check your input directory.")
        return
    logging.info(f"Found {len(classes)} classes.")
    
    diagram = generate_class_diagram(classes)
    
    png_path = os.path.join(current_dir, 'Combined_Java_Class_Diagram.png')
    safe_write_png(diagram, png_path)

    pdf_path = os.path.join(current_dir, 'Java_Class_Diagram_Report.pdf')
    generate_enhanced_pdf(png_path, pdf_path, classes)
    logging.info(f"PDF report generated: {pdf_path}")

if __name__ == "__main__":
    main()
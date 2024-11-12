import ast
import os
import logging
from dataclasses import dataclass
from typing import List, Dict
import plantuml
from datetime import datetime
import glob
import sys
import requests
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.units import inch

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@dataclass
class Message:
    from_participant: str
    to_participant: str
    message: str
    sequence_number: int
    message_type: str
    description: str = ""
    file_source: str = ""

class MultiFileSequenceDiagramGenerator:
    def __init__(self, directory: str = None):
        if directory is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            self.directory = os.path.join(project_root, 'testing', 'python_seq')
        else:
            self.directory = directory
            
        self.messages = []
        self.participants = set()
        self.sequence_number = 1
        self.files_analyzed = set()
        
        if not os.path.exists(self.directory):
            raise ValueError(f"Directory does not exist: {self.directory}")
        
        logging.info(f"Initialized with directory: {self.directory}")

    def analyze_directory(self):
        python_files = glob.glob(os.path.join(self.directory, "**/*.py"), recursive=True)
        
        if not python_files:
            logging.warning(f"No Python files found in {self.directory}")
            return {'warning':f'No Python files found in {self.directory}'}

        logging.info(f"Found {len(python_files)} Python files to analyze")
        for file_path in python_files:
            logging.info(f"Analyzing file: {os.path.basename(file_path)}")
            self.analyze_file(file_path)
        
        return len(self.files_analyzed) > 0

    def analyze_file(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    tree = ast.parse(file.read())
                    self._analyze_tree(tree, file_path)
                    self.files_analyzed.add(file_path)
                    logging.info(f"Successfully analyzed: {os.path.basename(file_path)}")
                    return {
                        'status':'message',
                        'message':f"Successfully analyzed: {os.path.basename(file_path)}"
                    }
                except SyntaxError as e:
                    logging.error(f"Syntax error in {file_path}: {e}")
                    return {
                        'status':'error',
                        'error':f'Syntax error in {file_path}: {e}'
                    }
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
            return {
                'status':'error',
                'error':f'Error reading file {file_path}: {e}'
            }

    def _analyze_tree(self, tree, file_path):
        class MethodVisitor(ast.NodeVisitor):
            def __init__(self, outer, source_file):
                self.outer = outer
                self.current_class = None
                self.current_method = None
                self.source_file = source_file

            def visit_ClassDef(self, node):
                self.current_class = node.name
                self.outer.participants.add(node.name)
                self.generic_visit(node)

            def visit_FunctionDef(self, node):
                self.current_method = node.name
                docstring = ast.get_docstring(node)
                
                for stmt in node.body:
                    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                        self._analyze_call(stmt.value, docstring)
                
                self.generic_visit(node)

            def _analyze_call(self, call, docstring=""):
                if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name):
                    from_participant = self.current_class or "System"
                    to_participant = call.func.value.id
                    message = call.func.attr
                    logging.info(f"Adding message from {from_participant} to {to_participant} with message '{message}'")
                    
                    message_type = 'dashed' if any(word in message.lower() 
                                                 for word in ['return', 'get', 'fetch', 'retrieve']) else 'solid'
                    
                    description = (f"Method '{message}' called from {from_participant} to {to_participant}\n"
                                 f"Source: {os.path.basename(self.source_file)}")
                    if docstring:
                        description += f"\nDescription: {docstring}"

                    self.outer.participants.add(to_participant)
                    self.outer.messages.append(Message(
                        from_participant=from_participant,
                        to_participant=to_participant,
                        message=f"{self.outer.sequence_number}: {message}",
                        sequence_number=self.outer.sequence_number,
                        message_type=message_type,
                        description=description,
                        file_source=self.source_file
                    ))
                    self.outer.sequence_number += 1

        visitor = MethodVisitor(self, file_path)
        visitor.visit(tree)
        

    def generate_plantuml(self) -> str:
        if not self.messages:
            logging.warning("No messages to generate diagram from")
            return ""

        plantuml_str = """
@startuml
!theme plain
skinparam backgroundColor white
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true
skinparam BoxPadding 10

skinparam participant {
    BorderColor black
    BackgroundColor white
    FontColor black
}

skinparam sequence {
    ArrowColor #28a745
    ArrowFontColor #28a745
    ArrowFontSize 12
    LifeLineBorderColor grey
    LifeLineBackgroundColor white
}

skinparam note {
    BorderColor gray
    BackgroundColor white
}
"""
        plantuml_str += "\nparticipant User\n"
        for participant in sorted(self.participants):
            if participant.lower() != 'user':
                plantuml_str += f"participant {participant}\n"

        for msg in self.messages:
            arrow = "->" if msg.message_type == 'solid' else "-->"
            plantuml_str += f"{msg.from_participant} {arrow} {msg.to_participant} : <color:#28a745>{msg.message}</color>\n"

        plantuml_str += "@enduml"
        return plantuml_str

    def _generate_diagram(self, plantuml_str: str) -> bytes:
        """Helper method to generate the diagram using PlantUML"""
        try:
            server = 'http://www.plantuml.com/plantuml/png/'
            pl = plantuml.PlantUML(url=server)
            png_data = pl.processes(plantuml_str)
            return png_data
        except Exception as e:
            logging.error(f"Error generating diagram: {e}")
            raise

    def generate_pdf(self, output_path: str = None):
        if not self.messages:
            logging.error("No messages to generate PDF from")
            return {
                'status':'error',
                'error':'No messages to generate PDF from'}

        if output_path is None:
            output_dir = os.path.join(self.directory, 'output')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f'sequence_diagram_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')

        try:
            # Generate diagram
            plantuml_str = self.generate_plantuml()
            if not plantuml_str:
                return {
                    'status':'error',
                    'error':'plantuml str not generated! Internal Server Error'
                }

            # Generate the diagram
            diagram_path = output_path.replace('.pdf', '.png')
            os.makedirs(os.path.dirname(diagram_path), exist_ok=True)

            # Get the PNG data
            png_data = self._generate_diagram(plantuml_str)
            
            # Save the PNG data
            with open(diagram_path, 'wb') as f:
                f.write(png_data)

            # Create PDF using ReportLab
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            # Get the stylesheet
            styles = getSampleStyleSheet()
            # Create custom styles
            styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=styles['Title'],
                fontSize=16,
                spaceAfter=30
            ))
            styles.add(ParagraphStyle(
                name='CustomHeading',
                parent=styles['Heading1'],
                fontSize=14,
                spaceAfter=20
            ))
            styles.add(ParagraphStyle(
                name='CustomBody',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=12
            ))

            # Build the document content
            story = []

            # Title
            story.append(Paragraph('Multi-File Sequence Diagram Documentation', styles['CustomTitle']))

            # Project information
            story.append(Paragraph(f'Project Directory: {self.directory}', styles['CustomBody']))
            story.append(Paragraph(f'Files Analyzed: {len(self.files_analyzed)}', styles['CustomBody']))
            story.append(Paragraph(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', styles['CustomBody']))
            story.append(Spacer(1, 20))

            # Analyzed Files section
            story.append(Paragraph('Analyzed Files:', styles['CustomHeading']))
            for file_path in sorted(self.files_analyzed):
                story.append(Paragraph(f'• {os.path.basename(file_path)}', styles['CustomBody']))
            story.append(Spacer(1, 20))

            # Add diagram
            if os.path.exists(diagram_path):
                img = Image(diagram_path)
                img.drawHeight = 6*inch
                img.drawWidth = 7.5*inch
                story.append(img)
                story.append(Spacer(1, 20))

            # Sequence Details section
            story.append(Paragraph('Sequence Details', styles['CustomHeading']))

            messages_by_file = {}
            for msg in self.messages:
                file_name = os.path.basename(msg.file_source)
                if file_name not in messages_by_file:
                    messages_by_file[file_name] = []
                messages_by_file[file_name].append(msg)

            for file_name, messages in messages_by_file.items():
                story.append(Paragraph(f'File: {file_name}', styles['CustomHeading']))
                
                for msg in messages:
                    # Create a table for each message
                    data = [
                        [Paragraph(f'Message {msg.sequence_number}:', styles['CustomBody'])],
                        [Paragraph(msg.description, styles['CustomBody'])]
                    ]
                    
                    t = Table(data, colWidths=[6.5*inch])
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('TOPPADDING', (0, 0), (-1, 0), 12),
                        ('BOTTOMPADDING', (0, 1), (-1, -1), 12),
                        ('TOPPADDING', (0, 1), (-1, -1), 12),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(t)
                    story.append(Spacer(1, 10))

            # Build the PDF
            doc.build(story)
            logging.info(f"Generated PDF sequence diagram: {output_path}")
            return {
                'status':'message',
                'message':f'Generated PDF sequence diagram: {output_path}'
            }

        except Exception as e:
            logging.error(f"Error in generate_pdf: {e}")
            return {
                'status':'error',
                'error':f'Error in generate_pdf: {e}'
            }
            
        finally:
            # Clean up temporary PNG file
            if os.path.exists(diagram_path):
                os.remove(diagram_path)
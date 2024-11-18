import os
import logging
from dataclasses import dataclass
import javalang
import plantuml
from datetime import datetime
import glob
import sys
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

class JavaSequenceDiagramGenerator:
    def __init__(self, directory: str = None):
        if directory is None:
            # Get the directory of the current script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Move up to parent directory
            project_root = os.path.dirname(current_dir)
            # Set input directory to testing/java
            self.directory = os.path.join(project_root, 'testing', 'java')
        else:
            self.directory = directory
            
        self.messages = []
        self.participants = set()
        self.sequence_number = 1
        self.files_analyzed = set()
        
        # Ensure the directory exists
        if not os.path.exists(self.directory):
            raise ValueError(f"Directory does not exist: {self.directory}")
        
        logging.info(f"Initialized with directory: {self.directory}")

    def analyze_directory(self):
        java_files = glob.glob(os.path.join(self.directory, "**/*.java"), recursive=True)
        
        if not java_files:
            logging.warning(f"No Java files found in {self.directory}")
            return False

        logging.info(f"Found {len(java_files)} Java files to analyze")
        for file_path in java_files:
            logging.info(f"Analyzing file: {os.path.basename(file_path)}")
            self.analyze_file(file_path)
        
        return len(self.files_analyzed) > 0

    def analyze_file(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    tree = javalang.parse.parse(file.read())
                    self._analyze_tree(tree, file_path)
                    self.files_analyzed.add(file_path)
                    logging.info(f"Successfully analyzed: {os.path.basename(file_path)}")
                except javalang.parser.JavaSyntaxError as e:
                    logging.error(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")

    def _analyze_tree(self, tree, file_path):
        current_class = None
        
        # Process package and imports if needed
        for path, node in tree.filter(javalang.tree.ClassDeclaration):
            current_class = node.name
            self.participants.add(current_class)
            
            # Analyze method declarations
            for method in node.methods:
                method_name = method.name
                javadoc = method.documentation if hasattr(method, 'documentation') else ""
                
                # Analyze method body for method invocations
                if method.body:
                    for _, method_inv in method.body.filter(javalang.tree.MethodInvocation):
                        # Get the target class/object if available
                        if hasattr(method_inv, 'qualifier') and method_inv.qualifier:
                            to_participant = method_inv.qualifier
                            
                            # Check if this is a method call on another object
                            message_type = 'dashed' if any(word in method_inv.member.lower() 
                                                         for word in ['get', 'fetch', 'retrieve', 'return']) else 'solid'
                            
                            description = (f"Method '{method_inv.member}' called from {current_class} to {to_participant}\n"
                                         f"Source: {os.path.basename(file_path)}")
                            if javadoc:
                                description += f"\nDescription: {javadoc}"

                            self.participants.add(to_participant)
                            self.messages.append(Message(
                                from_participant=current_class,
                                to_participant=to_participant,
                                message=f"{self.sequence_number}: {method_inv.member}",
                                sequence_number=self.sequence_number,
                                message_type=message_type,
                                description=description,
                                file_source=file_path
                            ))
                            self.sequence_number += 1

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
    LifeLineBorderColor lightgray
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
            return False

        if output_path is None:
            output_dir = os.path.join(self.directory, 'output')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f'sequence_diagram_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')

        try:
            # Generate diagram
            plantuml_str = self.generate_plantuml()
            if not plantuml_str:
                return False

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
            story.append(Paragraph('Java Sequence Diagram Documentation', styles['CustomTitle']))

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
            return True

        except Exception as e:
            logging.error(f"Error in generate_pdf: {e}")
            return False
            
        finally:
            # Clean up temporary PNG file
            if os.path.exists(diagram_path):
                os.remove(diagram_path)

def main():
    try:
        generator = JavaSequenceDiagramGenerator()
        if generator.analyze_directory():
            if generator.generate_pdf():
                logging.info("Sequence diagram generation completed successfully")
            else:
                logging.error("Failed to generate sequence diagram")
        else:
            logging.error("No files were analyzed successfully")
    except Exception as e:
        logging.error(f"Error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
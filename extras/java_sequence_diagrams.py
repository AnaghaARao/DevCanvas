import os
import re
import logging
from dataclasses import dataclass
from datetime import datetime
import glob
from typing import List, Set
import plantuml
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
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
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            self.directory = os.path.join(project_root, 'testing', 'java')
        else:
            self.directory = directory

        self.messages: List[Message] = []
        self.participants: Set[str] = set()
        self.sequence_number = 1
        self.files_analyzed: Set[str] = set()
        
        if not os.path.exists(self.directory):
            raise ValueError(f"Directory does not exist: {self.directory}")
        
        logging.info(f"Initialized with directory: {self.directory}")

    def _extract_class_name(self, content: str) -> str:
        """Extract class name using regex."""
        match = re.search(r'class\s+(\w+)', content)
        return match.group(1) if match else None

    def _extract_method_calls(self, content: str) -> List[tuple]:
        """Extract method calls using regex patterns."""
        # Pattern to match method calls like: objectName.methodName()
        pattern = r'(\w+)\s*\.\s*(\w+)\s*\('
        
        method_calls = []
        for match in re.finditer(pattern, content):
            object_name, method_name = match.groups()
            if object_name.lower() not in ['system', 'out', 'err']:  # Skip system calls
                method_calls.append((object_name, method_name))
        
        return method_calls

    def analyze_file(self, file_path: str) -> bool:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                # Extract class name
                class_name = self._extract_class_name(content)
                if not class_name:
                    logging.warning(f"Could not find class name in {file_path}")
                    return False

                self.participants.add(class_name)
                
                # Extract method calls
                method_calls = self._extract_method_calls(content)
                
                for object_name, method_name in method_calls:
                    self.participants.add(object_name)
                    
                    # Determine message type based on method name
                    message_type = 'dashed' if any(word in method_name.lower() 
                                                 for word in ['get', 'fetch', 'retrieve', 'return']) else 'solid'
                    
                    description = (f"Method '{method_name}' called from {class_name} to {object_name}\n"
                                 f"Source: {os.path.basename(file_path)}")
                    
                    self.messages.append(Message(
                        from_participant=class_name,
                        to_participant=object_name,
                        message=f"{self.sequence_number}: {method_name}",
                        sequence_number=self.sequence_number,
                        message_type=message_type,
                        description=description,
                        file_source=file_path
                    ))
                    self.sequence_number += 1
                
                self.files_analyzed.add(file_path)
                logging.info(f"Successfully analyzed: {os.path.basename(file_path)}")
                return True
                
        except Exception as e:
            logging.error(f"Error analyzing file {file_path}: {e}")
            return False

    def analyze_directory(self) -> bool:
        java_files = glob.glob(os.path.join(self.directory, "**/*.java"), recursive=True)
        
        if not java_files:
            logging.warning(f"No Java files found in {self.directory}")
            return False

        logging.info(f"Found {len(java_files)} Java files to analyze")
        success_count = 0
        
        for file_path in java_files:
            logging.info(f"Analyzing file: {os.path.basename(file_path)}")
            if self.analyze_file(file_path):
                success_count += 1
        
        return success_count > 0

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
"""
        # Add participants
        for participant in sorted(self.participants):
            plantuml_str += f"participant {participant}\n"

        # Add messages
        for msg in self.messages:
            arrow = "->" if msg.message_type == 'solid' else "-->"
            plantuml_str += f"{msg.from_participant} {arrow} {msg.to_participant} : {msg.message}\n"

        plantuml_str += "@enduml"
        return plantuml_str

    def generate_pdf(self, output_path: str = None) -> bool:
        if not self.messages:
            logging.error("No messages to generate PDF from")
            return False

        # Set output directory relative to input directory
        if output_path is None:
            output_dir = os.path.join(self.directory, 'output')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f'sequence_diagram_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')

        try:
            # Generate PlantUML diagram
            plantuml_str = self.generate_plantuml()
            if not plantuml_str:
                return False

            # Convert to PNG using PlantUML server
            server = plantuml.PlantUML(url='http://www.plantuml.com/plantuml/png/')
            png_data = server.processes(plantuml_str)

            # Save temporary PNG
            temp_png = output_path.replace('.pdf', '.png')
            with open(temp_png, 'wb') as f:
                f.write(png_data)

            # Create PDF
            doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=72)

            # Define styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=24,
                spaceAfter=30
            )

            # Build PDF content
            story = []
            story.append(Paragraph('Java Sequence Diagram', title_style))
            story.append(Spacer(1, 20))
            
            # Add the diagram
            img = Image(temp_png)
            img.drawHeight = 6*inch
            img.drawWidth = 7.5*inch
            story.append(img)

            # Build the PDF
            doc.build(story)
            
            # Clean up
            os.remove(temp_png)
            
            logging.info(f"Generated PDF sequence diagram: {output_path}")
            return True

        except Exception as e:
            logging.error(f"Error generating PDF: {e}")
            return False

def main():
    try:
        # Initialize with default directory structure
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        input_dir = os.path.join(project_root, 'testing', 'java')
        
        logging.info(f"Set input directory to: {input_dir}")
        
        generator = JavaSequenceDiagramGenerator(input_dir)
        if generator.analyze_directory():
            if generator.generate_pdf():
                logging.info("Sequence diagram generation completed successfully")
            else:
                logging.error("Failed to generate sequence diagram")
        else:
            logging.error("No files were analyzed successfully")
    except Exception as e:
        logging.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()
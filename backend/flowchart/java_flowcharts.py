import os
import sys
import javalang
import pydot
import logging
import multiprocessing
from django.conf import settings
from typing import Dict, List, Tuple, Optional
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, 
    Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MethodInfo:
    def __init__(self, name: str):
        self.name = name
        self.statements: Optional[List[javalang.ast.Node]] = None

class ClassInfo:
    def __init__(self, name: str):
        self.name = name
        self.methods: Dict[str, MethodInfo] = {}

class JavaFlowchartGenerator:
    def __init__(self, directory, author, doc_id):
        # self.file_path = file_path
        self.author = author
        self.doc_id = doc_id
        self.directory = f'{settings.MEDIA_ROOT}/{self.author}/{directory}'

    def safe_write_png(self, graph, output_path):
        current_dir = self.directory
        filename = os.path.splitext(os.path.basename(output_path))[0]
        try:
            graph.write_png(output_path)
            logging.info(f"Generated: {output_path}")
        except Exception as e:
            logging.error(f"Error writing {filename}: {str(e)}")

    def analyze_java_file(self, file_path: str) -> Dict[str, ClassInfo]:
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
            
            for method in node.methods:
                method_info = MethodInfo(method.name)
                if method.body:
                    method_info.statements = method.body
                class_info.methods[method.name] = method_info
            
            classes[class_name] = class_info
        
        return classes

    def list_java_files(self) -> List[str]:
        java_files = []
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith('.java'):
                    file_path = os.path.join(root, file)
                    logging.info(f"Found Java file: {file_path}")
                    print(file_path)
                    java_files.append(file_path)
        return java_files

    def analyze_directory(self) -> Dict[str, ClassInfo]:
        all_classes = {}
        file_paths = self.list_java_files()
        
        with multiprocessing.Pool() as pool:
            results = pool.map(self.analyze_java_file, file_paths)
            for result in results:
                all_classes.update(result)
        
        return all_classes

    def generate_method_flowchart(self, method_info: MethodInfo) -> Optional[pydot.Dot]:
        if not method_info.statements:
            return None

        graph = pydot.Dot(graph_type='digraph', rankdir='TB', ratio='compress', size='8,8')
        graph.set_node_defaults(shape='rectangle', style='rounded', height='0.4', width='2')

        start = pydot.Node("start", label="Start", shape="ellipse")
        graph.add_node(start)

        end = pydot.Node("end", label="End", shape="ellipse")

        prev_node = start
        for i, stmt in enumerate(method_info.statements):
            if isinstance(stmt, javalang.tree.IfStatement):
                if_node = pydot.Node(f"if_{i}", label=f"If\n{stmt.condition}", shape="diamond")
                graph.add_node(if_node)
                graph.add_edge(pydot.Edge(prev_node, if_node))
                
                true_node = pydot.Node(f"true_{i}", label="True")
                false_node = pydot.Node(f"false_{i}", label="False")
                graph.add_node(true_node)
                graph.add_node(false_node)
                
                graph.add_edge(pydot.Edge(if_node, true_node, label="Yes"))
                graph.add_edge(pydot.Edge(if_node, false_node, label="No"))
                
                prev_node = if_node
            elif isinstance(stmt, (javalang.tree.ForStatement, javalang.tree.WhileStatement)):
                loop_node = pydot.Node(f"loop_{i}", label=f"{type(stmt).__name__[:-9]} loop", shape="diamond")
                graph.add_node(loop_node)
                graph.add_edge(pydot.Edge(prev_node, loop_node))
                prev_node = loop_node
            elif isinstance(stmt, javalang.tree.TryStatement):
                try_node = pydot.Node(f"try_{i}", label="Try", shape="rectangle")
                graph.add_node(try_node)
                graph.add_edge(pydot.Edge(prev_node, try_node))
                prev_node = try_node
            elif isinstance(stmt, javalang.tree.CatchClause):
                catch_node = pydot.Node(f"catch_{i}", label=f"Catch {stmt.parameter.name}", shape="rectangle")
                graph.add_node(catch_node)
                graph.add_edge(pydot.Edge(prev_node, catch_node))
                prev_node = catch_node
            else:
                node = pydot.Node(f"stmt_{i}", label=type(stmt).__name__[:-9])
                graph.add_node(node)
                graph.add_edge(pydot.Edge(prev_node, node))
                prev_node = node

        graph.add_node(end)
        graph.add_edge(pydot.Edge(prev_node, end))

        return graph

    def generate_flowcharts(self, classes: Dict[str, ClassInfo]) -> Dict[str, Dict[str, Optional[pydot.Dot]]]:
        flowcharts = {}
        for class_name, class_info in classes.items():
            flowcharts[class_name] = {}
            for method_name, method_info in class_info.methods.items():
                flowchart = self.generate_method_flowchart(method_info)
                if flowchart:
                    flowcharts[class_name][method_name] = flowchart
        return flowcharts
    
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

    def calculate_method_complexity(method_info: MethodInfo):
        """Advanced method complexity calculation"""
        complexity = 1  # Base complexity
        statement_types = {}
        
        for stmt in method_info.statements or []:
            # Increment complexity for control flow statements
            if isinstance(stmt, (javalang.tree.IfStatement, 
                                javalang.tree.WhileStatement, 
                                javalang.tree.ForStatement, 
                                javalang.tree.TryStatement,
                                javalang.tree.SwitchStatement)):
                complexity += 1
            
            # Track statement types
            stmt_type = type(stmt).__name__
            statement_types[stmt_type] = statement_types.get(stmt_type, 0) + 1
            
            # Estimate lines of code (very basic)
            method_info.lines_of_code += 1
        
        method_info.complexity = complexity
        method_info.statement_types = statement_types
        return complexity

    def generate_metrics_data(classes: Dict[str, ClassInfo]) -> List[List[str]]:
        """Generate comprehensive project metrics"""
        total_classes = len(classes)
        total_methods = sum(class_info.method_count for class_info in classes.values())
        
        metrics_data = [
            ['Metric', 'Value'],
            ['Total Classes', str(total_classes)],
            ['Total Methods', str(total_methods)],
            ['Avg Methods per Class', f'{total_methods/total_classes:.2f}' if total_classes else 'N/A'],
            ['Total Complexity', str(sum(class_info.total_method_complexity for class_info in classes.values()))],
            ['Avg Method Complexity', f'{sum(class_info.total_method_complexity for class_info in classes.values())/total_methods:.2f}' if total_methods else 'N/A']
        ]
        return metrics_data

    def generate_pdf(self, flowcharts, output_path, classes):
        """Comprehensive PDF generation with improved formatting"""
        try:
            doc = SimpleDocTemplate(
                output_path, 
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=110,
                bottomMargin=72
            )
            
            styles = getSampleStyleSheet()
            
            # Create custom style for better spacing
            styles.add(ParagraphStyle(
                name='TitleSpacing',
                parent=styles['Title'],
                spaceAfter=18,
                spaceBefore=12
            ))
            
            styles.add(ParagraphStyle(
                name='SectionSpacing',
                parent=styles['Heading2'],
                spaceAfter=12,
                spaceBefore=18
            ))
            
            styles.add(ParagraphStyle(
                name='SubsectionSpacing',
                parent=styles['Heading3'],
                spaceAfter=6,
                spaceBefore=12
            ))
            
            story = []

            # Title with improved spacing
            story.append(Paragraph("Java Flowcharts & Analysis Report", styles['TitleSpacing']))
            story.append(Spacer(1, 12))
            
            # Metrics Section
            metrics_data = self.generate_metrics_data(classes)
            metrics_table = Table(metrics_data, colWidths=[3*inch, 3*inch])
            metrics_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.gray),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ]))
            
            story.append(Paragraph("Project Metrics", styles['SectionSpacing']))
            story.append(metrics_table)
            story.append(PageBreak())

            # Flowchart Generation
            for class_name, methods in flowcharts.items():
                # Class level section with improved spacing
                class_title = Paragraph(f"Class: {class_name}", styles['SectionSpacing'])
                story.append(class_title)
                
                for method_name, flowchart in methods.items():
                    # Method level subsection with improved spacing
                    method_title = Paragraph(f"Method: {method_name}", styles['SubsectionSpacing'])
                    story.append(method_title)
                    
                    if flowchart:
                        png_path = self.safe_write_png(flowchart, f"{class_name}_{method_name}_flowchart.png")
                        if png_path:
                            img = Image(png_path, width=6*inch, height=4*inch)
                            story.append(img)
                    else:
                        story.append(Paragraph("No flowchart available", styles['Normal']))
                    
                    story.append(Spacer(1, 12))

            doc.build(story, onFirstPage=self.create_header_footer, onLaterPages=self.create_header_footer)
            print('pdf successfully generated')
            return {'message':'pdf successfully generated'}
        except Exception as e:
            return {'error':'error in generating pdf'}
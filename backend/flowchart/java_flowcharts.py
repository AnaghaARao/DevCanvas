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
import tempfile

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

    def generate_method_flowchart(self, method_info: MethodInfo, method_name: str):
        if not method_info.statements:
            return None

        graph = pydot.Dot(graph_type='digraph', rankdir='TB', ratio='compress', size='8,8')
        graph.set_node_defaults(shape='rectangle', style='rounded', height='0.4', width='2')

        # Create start and end nodes
        start = pydot.Node("start", label="Start", shape="ellipse", style="filled", fillcolor="lightgreen")
        graph.add_node(start)

        end = pydot.Node("end", label="End", shape="ellipse", style="filled", fillcolor="lightcoral")
        graph.add_node(end)

        # Track the previous node to create connections
        prev_node = start
        final_node = start

        def add_node_with_connection(self, node, connection_node=None):
            nonlocal prev_node, final_node
            graph.add_node(node)
            if connection_node:
                graph.add_edge(pydot.Edge(connection_node, node))
            else:
                graph.add_edge(pydot.Edge(prev_node, node))
            prev_node = node
            final_node = node

        def process_block(statements, parent_node=None):
            nonlocal prev_node, final_node
            for i, stmt in enumerate(statements):
                if isinstance(stmt, javalang.tree.IfStatement):
                    # Create if-else diamond node
                    if_node = pydot.Node(f"if_{method_name}_{i}", 
                                        label=f"If\n{stmt.condition}", 
                                        shape="diamond", 
                                        style="filled", 
                                        fillcolor="lightyellow")
                    
                    # Connect to previous node
                    if parent_node:
                        graph.add_edge(pydot.Edge(parent_node, if_node))
                    else:
                        graph.add_edge(pydot.Edge(prev_node, if_node))

                    # True branch
                    true_block_node = pydot.Node(f"true_block_{method_name}_{i}", 
                                                label="True Block", 
                                                shape="rectangle")
                    graph.add_node(true_block_node)
                    graph.add_edge(pydot.Edge(if_node, true_block_node, label="Yes"))

                    # Process true block
                    if stmt.then_statement:
                        process_block([stmt.then_statement], true_block_node)

                    # False branch
                    false_block_node = pydot.Node(f"false_block_{method_name}_{i}", 
                                                label="False Block", 
                                                shape="rectangle")
                    graph.add_node(false_block_node)
                    graph.add_edge(pydot.Edge(if_node, false_block_node, label="No"))

                    # Process false block if exists
                    if stmt.else_statement:
                        process_block([stmt.else_statement], false_block_node)

                    prev_node = if_node

                elif isinstance(stmt, (javalang.tree.ForStatement, javalang.tree.WhileStatement)):
                    # Create loop node
                    loop_node = pydot.Node(f"loop_{method_name}_{i}", 
                                        label=f"{type(stmt).__name__[:-9]} Loop\n{stmt.condition or ''}", 
                                        shape="diamond", 
                                        style="filled", 
                                        fillcolor="lightblue")
                    
                    # Connect to previous node
                    if parent_node:
                        graph.add_edge(pydot.Edge(parent_node, loop_node))
                    else:
                        graph.add_edge(pydot.Edge(prev_node, loop_node))

                    # Loop body
                    loop_body_node = pydot.Node(f"loop_body_{method_name}_{i}", 
                                                label="Loop Body", 
                                                shape="rectangle")
                    graph.add_node(loop_body_node)
                    graph.add_edge(pydot.Edge(loop_node, loop_body_node, label="Iterate"))

                    # Process loop body
                    if stmt.body:
                        process_block([stmt.body], loop_body_node)

                    # Connect back to loop
                    graph.add_edge(pydot.Edge(loop_body_node, loop_node, style="dashed"))

                    prev_node = loop_node

                elif isinstance(stmt, javalang.tree.TryStatement):
                    # Try block
                    try_node = pydot.Node(f"try_{method_name}_{i}", 
                                        label="Try Block", 
                                        shape="rectangle", 
                                        style="filled", 
                                        fillcolor="lightcyan")
                    
                    # Connect to previous node
                    if parent_node:
                        graph.add_edge(pydot.Edge(parent_node, try_node))
                    else:
                        graph.add_edge(pydot.Edge(prev_node, try_node))

                    # Process try block
                    if stmt.block:
                        process_block(stmt.block, try_node)

                    # Process catch blocks
                    for catch in stmt.catches:
                        catch_node = pydot.Node(f"catch_{method_name}_{i}", 
                                                label=f"Catch {catch.parameter.type.name}", 
                                                shape="rectangle", 
                                                style="filled", 
                                                fillcolor="lightsalmon")
                        graph.add_node(catch_node)
                        graph.add_edge(pydot.Edge(try_node, catch_node))

                        # Process catch block
                        if catch.block:
                            process_block(catch.block, catch_node)

                    prev_node = try_node

                elif isinstance(stmt, javalang.tree.ReturnStatement):
                    return_node = pydot.Node(f"return_{method_name}_{i}", 
                                            label=f"Return\n{stmt.expression}", 
                                            shape="parallelogram", 
                                            style="filled", 
                                            fillcolor="lightpink")
                    
                    # Connect to previous node
                    if parent_node:
                        graph.add_edge(pydot.Edge(parent_node, return_node))
                    else:
                        graph.add_edge(pydot.Edge(prev_node, return_node))

                    # Connect to end
                    graph.add_edge(pydot.Edge(return_node, end))

                    prev_node = return_node

                else:
                    # Generic statement node
                    stmt_node = pydot.Node(f"stmt_{method_name}_{i}", 
                                        label=type(stmt).__name__[:-9], 
                                        shape="rectangle")
                    
                    # Connect to previous node
                    if parent_node:
                        graph.add_edge(pydot.Edge(parent_node, stmt_node))
                    else:
                        graph.add_edge(pydot.Edge(prev_node, stmt_node))

                    prev_node = stmt_node

        # Process all statements
        process_block(method_info.statements)

        # Connect last node to end if not already connected
        graph.add_node(end)
        graph.add_edge(pydot.Edge(final_node, end))

        return graph

    
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

    # def calculate_method_complexity(method_info: MethodInfo):
    #     """Advanced method complexity calculation"""
    #     complexity = 1  # Base complexity
    #     statement_types = {}
        
    #     for stmt in method_info.statements or []:
    #         # Increment complexity for control flow statements
    #         if isinstance(stmt, (javalang.tree.IfStatement, 
    #                             javalang.tree.WhileStatement, 
    #                             javalang.tree.ForStatement, 
    #                             javalang.tree.TryStatement,
    #                             javalang.tree.SwitchStatement)):
    #             complexity += 1
            
    #         # Track statement types
    #         stmt_type = type(stmt).__name__
    #         statement_types[stmt_type] = statement_types.get(stmt_type, 0) + 1
            
    #         # Estimate lines of code (very basic)
    #         method_info.lines_of_code += 1
        
    #     method_info.complexity = complexity
    #     method_info.statement_types = statement_types
    #     return complexity

    # def generate_metrics_data(self, classes: Dict[str, ClassInfo]) -> List[List[str]]:
    #     """Generate comprehensive project metrics"""
    #     total_classes = len(classes)
    #     total_methods = sum(class_info.method_count for class_info in classes.values())
        
    #     metrics_data = [
    #         ['Metric', 'Value'],
    #         ['Total Classes', str(total_classes)],
    #         ['Total Methods', str(total_methods)],
    #         ['Avg Methods per Class', f'{total_methods/total_classes:.2f}' if total_classes else 'N/A'],
    #         ['Total Complexity', str(sum(class_info.total_method_complexity for class_info in classes.values()))],
    #         ['Avg Method Complexity', f'{sum(class_info.total_method_complexity for class_info in classes.values())/total_methods:.2f}' if total_methods else 'N/A']
    #     ]
    #     return metrics_data

    def generate_flowcharts(self, classes: Dict[str, ClassInfo]) -> Dict[str, Dict[str, Optional[pydot.Dot]]]:
        flowcharts = {}
        for class_name, class_info in classes.items():
            flowcharts[class_name] = {}
            for method_name, method_info in class_info.methods.items():
                flowchart = self.generate_method_flowchart(method_info, method_name)
                if flowchart:
                    flowcharts[class_name][method_name] = flowchart
        return flowcharts

    def generate_pdf(self, flowcharts, output_path):
        """Comprehensive PDF generation with improved formatting"""
        print("generating pdf!")
        try:
            print("within try block")
            temp_dir = self.directory  # Use self.directory instead of creating a temp dir
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)  # Ensure the directory exists

            doc = SimpleDocTemplate(output_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            title = Paragraph("Java Method Flowcharts", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))

            for class_name, methods in flowcharts.items():
                class_title = Paragraph(f"Class: {class_name}", styles['Heading2'])
                story.append(class_title)

                for method_name, flowchart in methods.items():
                    method_title = Paragraph(f"Method: {method_name}", styles['Heading3'])
                    story.append(method_title)

                    try:
                        if flowchart:
                            # Save PNG within self.directory
                            png_path = os.path.join(temp_dir, f"{class_name}_{method_name}_flowchart.png")
                            self.safe_write_png(flowchart, png_path)

                            # Add the image to the PDF
                            img = Image(png_path, width=6 * inch, height=4 * inch)
                            story.append(img)
                        else:
                            story.append(Paragraph("No flowchart available (abstract method or interface)", styles['Normal']))
                    except Exception as e:
                        print(f"Error handling flowchart for {method_name}: {e}")

                    story.append(Spacer(1, 12))

            # Build the PDF
            doc.build(story, onFirstPage=self.create_header_footer, onLaterPages=self.create_header_footer)
            print('PDF successfully generated')
            print('Output path:', output_path)
            return {'message': 'PDF successfully generated'}
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return {'error': str(e)}

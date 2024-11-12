import ast
import pydot
import os
import sys
import logging
import multiprocessing
from django.conf import settings
from typing import Dict, List, Tuple, Union
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FunctionInfo:
    def __init__(self, name: str):
        self.name = name
        self.statements: List[ast.AST] = []

class ClassInfo:
    def __init__(self, name: str):
        self.name = name
        self.methods: Dict[str, FunctionInfo] = {}

# current_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.dirname(current_dir)
# input_dir = os.path.join(project_root, 'testing', 'pythonTesting')


class PythonFlowchartGenerator:
    def __init__(self, file_path, author, doc_id):
        self.file_path = file_path
        self.author = author
        self.doc_id = doc_id

    def safe_write_png(self, graph):
        current_dir = f"{settings.MEDIA_URL}/{self.author}"
        filename = os.path.splitext(os.path.basename(self.file_path))[0]
        output_path = os.path.join(current_dir, filename)
        try:
            graph.write_png(output_path)
            logging.info(f"Generated: {output_path}")
            # return {'img_path':output_path}
        except Exception as e:
            logging.error(f"Error writing {filename}: {str(e)}")
            # return {'error':f'Error writing {filename}: {str(e)}'}

    def analyze_file(self):
        elements = {}
        filename = os.path.splitext(os.path.basename(self.file_path))[0]
        with open(self.file_path, 'r') as file:
            try:
                tree = ast.parse(file.read(), filename)
            except SyntaxError as e:
                logging.error(f"Syntax error in {self.file_path}: {e}")
                return {'error':f'Syntax error in {self.file_path}: {e}'}

            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    class_info = ClassInfo(class_name)
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = FunctionInfo(item.name)
                            method_info.statements = item.body
                            class_info.methods[item.name] = method_info
                    
                    elements[class_name] = class_info
                elif isinstance(node, ast.FunctionDef):
                    function_name = node.name
                    function_info = FunctionInfo(function_name)
                    function_info.statements = node.body
                    elements[function_name] = function_info

        return elements

    def list_python_files(self, directory: str) -> List[str]:
        python_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        return python_files

    def analyze_directory(self, directory: str) -> Dict[str, Union[ClassInfo, FunctionInfo]]:
        all_elements = {}
        file_paths = self.list_python_files(directory)
        
        with multiprocessing.Pool() as pool:
            results = pool.map(self.analyze_python_file, file_paths)
            for result in results:
                all_elements.update(result)
        
        return all_elements

    def generate_flowchart(self, func_info: FunctionInfo) -> pydot.Dot:
        graph = pydot.Dot(graph_type='digraph', rankdir='TB', ratio='compress', size='8,8')
        graph.set_node_defaults(shape='rectangle', style='rounded', height='0.4', width='2')

        start = pydot.Node("start", label="Start", shape="ellipse")
        graph.add_node(start)

        end = pydot.Node("end", label="End", shape="ellipse")

        prev_node = start
        for i, stmt in enumerate(func_info.statements):
            if isinstance(stmt, ast.If):
                if_node = pydot.Node(f"if_{i}", label=f"If\n{ast.unparse(stmt.test)}", shape="diamond")
                graph.add_node(if_node)
                graph.add_edge(pydot.Edge(prev_node, if_node))
                
                true_node = pydot.Node(f"true_{i}", label="True")
                false_node = pydot.Node(f"false_{i}", label="False")
                graph.add_node(true_node)
                graph.add_node(false_node)
                
                graph.add_edge(pydot.Edge(if_node, true_node, label="Yes"))
                graph.add_edge(pydot.Edge(if_node, false_node, label="No"))
                
                prev_node = if_node
            elif isinstance(stmt, (ast.For, ast.While)):
                loop_node = pydot.Node(f"loop_{i}", label=f"{type(stmt).__name__} loop", shape="diamond")
                graph.add_node(loop_node)
                graph.add_edge(pydot.Edge(prev_node, loop_node))
                prev_node = loop_node
            else:
                node = pydot.Node(f"stmt_{i}", label=type(stmt).__name__)
                graph.add_node(node)
                graph.add_edge(pydot.Edge(prev_node, node))
                prev_node = node

        graph.add_node(end)
        graph.add_edge(pydot.Edge(prev_node, end))

        return graph
        

    def generate_flowcharts(self, elements: Dict[str, Union[ClassInfo, FunctionInfo]]) -> Dict[str, Union[Dict[str, pydot.Dot], pydot.Dot]]:
        flowcharts = {}
        for name, element in elements.items():
            if isinstance(element, ClassInfo):
                flowcharts[name] = {}
                for method_name, method_info in element.methods.items():
                    flowcharts[name][method_name] = self.generate_flowchart(method_info)
            elif isinstance(element, FunctionInfo):
                flowcharts[name] = self.generate_flowchart(element)
        return flowcharts

    def generate_pdf(self, flowcharts: Dict[str, Union[Dict[str, pydot.Dot], pydot.Dot]], output_path: str):
        current_dir = f"{settings.MEDIA_URL}/{self.author}"
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        title = Paragraph("Python Flowcharts", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))

        for name, item in flowcharts.items():
            if isinstance(item, dict):  # Class
                class_title = Paragraph(f"Class: {name}", styles['Heading2'])
                story.append(class_title)
                
                for method_name, flowchart in item.items():
                    method_title = Paragraph(f"Method: {method_name}", styles['Heading3'])
                    story.append(method_title)
                    
                    png_path = os.path.join(current_dir, f"{name}_{method_name}_flowchart.png")
                    self.safe_write_png(flowchart, png_path)
                    
                    img = Image(png_path, width=6*inch, height=4*inch)
                    story.append(img)
                    story.append(Spacer(1, 12))
            else:  # Function
                function_title = Paragraph(f"Function: {name}", styles['Heading2'])
                story.append(function_title)
                
                png_path = os.path.join(current_dir, f"{name}_flowchart.png")
                self.safe_write_png(item, png_path)
                
                img = Image(png_path, width=6*inch, height=4*inch)
                story.append(img)
                story.append(Spacer(1, 12))

        doc.build(story)

    # def main(self):
    #     logging.info(f"Analyzing file: {self.file_path}")
    #     classes = self.analyze_file()
        
    #     if not classes:
    #         logging.error("No classes or functions found in the specified directory. Please check your input directory.")
    #         return{
    #             'error':"No classes or functions found in the specified file path"
    #         }
    #     logging.info(f"Found {len(classes)} classes and functions.")
    #     return {'success':f'Found {classes} classes and functions.'}
        
    #     flowcharts = self.generate_flowcharts(classes)
        
    #     pdf_path = os.path.join(current_dir, 'Python_Flowcharts_Report.pdf')
    #     self.generate_pdf(flowcharts, pdf_path)
    #     logging.info(f"PDF report generated: {pdf_path}")

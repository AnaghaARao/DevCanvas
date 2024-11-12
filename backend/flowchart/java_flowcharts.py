import os
import sys
import javalang
import pydot
import logging
import multiprocessing
from django.conf import settings
from typing import Dict, List, Tuple, Optional
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

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
    def __init__(self, file_path, author, doc_id):
        self.file_path = file_path
        self.author = author
        self.doc_id = doc_id

    def safe_write_png(self, graph, filename):
        current_dir = f"{settings.MEDIA_URL}/{self.author}"
        output_path = os.path.join(current_dir, filename)
        try:
            graph.write_png(output_path)
            logging.info(f"Generated: {output_path}")
        except Exception as e:
            logging.error(f"Error writing {filename}: {str(e)}")

    def analyze_file(self) -> Dict[str, ClassInfo]:
        classes = {}
        with open(self.file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        try:
            tree = javalang.parse.parse(content)
        except javalang.parser.JavaSyntaxError:
            logging.error(f"Syntax error in file: {self.file_path}")
            return {'error':f"Syntax error in file: {self.file_path}"}

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

    def list_java_files(self, directory: str) -> List[str]:
        java_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.java'):
                    java_files.append(os.path.join(root, file))
        return java_files

    def analyze_directory(self, directory: str) -> Dict[str, ClassInfo]:
        all_classes = {}
        file_paths = self.list_java_files(directory)
        
        with multiprocessing.Pool() as pool:
            results = pool.map(self.analyze_file, file_paths)
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

    def generate_pdf(self, flowcharts: Dict[str, Dict[str, Optional[pydot.Dot]]], output_path: str):
        current_dir = f"{settings.MEDIA_URL}/{self.author}"
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        title = Paragraph("Java Flowcharts", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))

        for class_name, methods in flowcharts.items():
            class_title = Paragraph(f"Class: {class_name}", styles['Heading2'])
            story.append(class_title)
            
            for method_name, flowchart in methods.items():
                method_title = Paragraph(f"Method: {method_name}", styles['Heading3'])
                story.append(method_title)
                
                if flowchart:
                    png_path = os.path.join(current_dir, f"{class_name}_{method_name}_flowchart.png")
                    self.safe_write_png(flowchart, png_path)
                    
                    img = Image(png_path, width=6*inch, height=4*inch)
                    story.append(img)
                else:
                    story.append(Paragraph("No flowchart available (abstract method or interface)", styles['Normal']))
                
                story.append(Spacer(1, 12))

        doc.build(story)

    # def main():
    #     logging.info(f"Analyzing directory: {input_dir}")
    #     classes = analyze_directory(input_dir)
        
    #     if not classes:
    #         logging.error("No classes found in the specified directory. Please check your input directory.")
    #         return
    #     logging.info(f"Found {len(classes)} classes.")
        
    #     flowcharts = generate_class_flowcharts(classes)
        
    #     pdf_path = os.path.join(current_dir, 'Java_Flowcharts_Report.pdf')
    #     generate_pdf(flowcharts, pdf_path)
    #     logging.info(f"PDF report generated: {pdf_path}")

    # if __name__ == "__main__":
    #     main()
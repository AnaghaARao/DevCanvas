import os
import sys
import javalang
import pydot
import logging
import multiprocessing
from typing import Dict, List, Tuple, Optional
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
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

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
input_dir = os.path.join(project_root, 'testing', 'java')

def safe_write_png(graph, filename):
    output_path = os.path.join(current_dir, filename)
    try:
        graph.write_png(output_path)
        logging.info(f"Generated: {output_path}")
    except Exception as e:
        logging.error(f"Error writing {filename}: {str(e)}")

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
        
        for method in node.methods:
            method_info = MethodInfo(method.name)
            if method.body:
                method_info.statements = method.body
            class_info.methods[method.name] = method_info
        
        classes[class_name] = class_info
    
    return classes

def list_java_files(directory: str) -> List[str]:
    java_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.java'):
                java_files.append(os.path.join(root, file))
    return java_files

def analyze_directory(directory: str) -> Dict[str, ClassInfo]:
    all_classes = {}
    file_paths = list_java_files(directory)
    
    with multiprocessing.Pool() as pool:
        results = pool.map(analyze_java_file, file_paths)
        for result in results:
            all_classes.update(result)
    
    return all_classes

def generate_method_flowchart(method_info: MethodInfo, method_name: str) -> Optional[pydot.Dot]:
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

    def add_node_with_connection(node, connection_node=None):
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

def generate_class_flowcharts(classes: Dict[str, ClassInfo]) -> Dict[str, Dict[str, Optional[pydot.Dot]]]:
    flowcharts = {}
    for class_name, class_info in classes.items():
        flowcharts[class_name] = {}
        for method_name, method_info in class_info.methods.items():
            flowchart = generate_method_flowchart(method_info, method_name)
            if flowchart:
                flowcharts[class_name][method_name] = flowchart
    return flowcharts

def generate_pdf(flowcharts: Dict[str, Dict[str, Optional[pydot.Dot]]], output_path: str):
    # Create a temporary directory to store intermediate PNG files
    with tempfile.TemporaryDirectory() as temp_dir:
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
                
                if flowchart:
                    png_path = os.path.join(temp_dir, f"{class_name}_{method_name}_flowchart.png")
                    flowchart.write_png(png_path)
                    
                    img = Image(png_path, width=6*inch, height=4*inch)
                    story.append(img)
                else:
                    story.append(Paragraph("No flowchart available (abstract method or interface)", styles['Normal']))
                
                story.append(Spacer(1, 12))

        doc.build(story)

def main():
    logging.info(f"Analyzing directory: {input_dir}")
    classes = analyze_directory(input_dir)
    
    if not classes:
        logging.error("No classes found in the specified directory. Please check your input directory.")
        return
    logging.info(f"Found {len(classes)} classes.")
    
    flowcharts = generate_class_flowcharts(classes)
    
    pdf_path = os.path.join(current_dir, 'Java_Flowcharts_Report.pdf')
    generate_pdf(flowcharts, pdf_path)
    logging.info(f"PDF report generated: {pdf_path}")

if __name__ == "__main__":
    main()
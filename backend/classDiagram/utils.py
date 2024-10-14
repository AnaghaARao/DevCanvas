import os
import pydot
import javalang

# Function to analyze Java file and extract classes and methods
def analyze_java_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    try:
        tree = javalang.parse.parse(content)
    except javalang.parser.JavaSyntaxError:
        print(f"Syntax error in file: {file_path}")
        return None, None

    classes = {}
    methods = {}

    for path, node in tree.filter(javalang.tree.ClassDeclaration):
        class_name = node.name
        class_methods = [m.name for m in node.methods]
        base_class = node.extends.name if node.extends else None
        interfaces = [i.name for i in node.implements] if node.implements else []
        classes[class_name] = {
            'methods': class_methods,
            'base_class': base_class,
            'interfaces': interfaces
        }

        for method in node.methods:
            methods[f"{class_name}.{method.name}"] = analyze_method_flow(method)

    return classes, methods

# Function to analyze method flow for flowchart
def analyze_method_flow(method):
    flow = []
    for path, node in method.filter(javalang.tree.Statement):
        if isinstance(node, javalang.tree.IfStatement):
            flow.append(('decision', node.condition))
            if node.else_statement:
                flow.append(('else', None))
        elif isinstance(node, javalang.tree.ReturnStatement):
            flow.append(('return', node.expression))
        elif isinstance(node, javalang.tree.LocalVariableDeclaration):
            for declarator in node.declarators:
                if declarator.initializer:
                    flow.append(('process', f"{node.type.name} {declarator.name} = {declarator.initializer}"))
        elif isinstance(node, javalang.tree.ForStatement):
            flow.append(('loop', f'for ({node.init}; {node.condition}; {node.update})'))
        elif isinstance(node, javalang.tree.WhileStatement):
            flow.append(('loop', f'while ({node.condition})'))
        elif isinstance(node, javalang.tree.DoStatement):
            flow.append(('loop', f'do while ({node.condition})'))
    return flow

# Function to generate class diagram using pydot
def generate_class_diagram(all_classes):
    graph = pydot.Dot(graph_type='digraph')
    graph.set_rankdir('TB')
    graph.set_size('12,12')

    for file_name, classes in all_classes.items():
        for class_name, class_info in classes.items():
            methods = class_info['methods']
            method_str = '\\n'.join(methods)
            node = pydot.Node(class_name, label=f'{{{class_name}|{method_str}}}', shape='record')
            graph.add_node(node)

    for file_name, classes in all_classes.items():
        for class_name, class_info in classes.items():
            if class_info['base_class']:
                edge = pydot.Edge(class_info['base_class'], class_name, label='extends')
                graph.add_edge(edge)

    return graph

# Function to generate flowchart using pydot
def generate_flowchart(method_name, flow):
    graph = pydot.Dot(graph_type='digraph')
    graph.set_rankdir('TB')
    graph.set_size('12,12')

    graph.add_node(pydot.Node('start', label='Start', shape='ellipse'))
    prev_node = 'start'
    stack = []

    for i, (step_type, step_info) in enumerate(flow):
        node_id = f'node_{i}'
        if step_type == 'decision':
            graph.add_node(pydot.Node(node_id, label=str(step_info), shape='diamond'))
            graph.add_edge(pydot.Edge(prev_node, node_id))
            stack.append((node_id, 'decision'))
            prev_node = node_id
        elif step_type == 'else':
            prev_decision, _ = stack.pop()
            prev_node = f'{prev_decision}_no'
        elif step_type == 'return':
            graph.add_node(pydot.Node(node_id, label=f'Return {step_info}', shape='box'))
            graph.add_edge(pydot.Edge(prev_node, node_id))
            prev_node = node_id
            graph.add_edge(pydot.Edge(node_id, 'end'))
        elif step_type == 'process':
            graph.add_node(pydot.Node(node_id, label=str(step_info), shape='box'))
            graph.add_edge(pydot.Edge(prev_node, node_id))
            prev_node = node_id
        elif step_type == 'loop':
            graph.add_node(pydot.Node(node_id, label=str(step_info), shape='box'))
            graph.add_edge(pydot.Edge(prev_node, node_id))
            prev_node = node_id
            stack.append((node_id, 'loop'))

    graph.add_node(pydot.Node('end', label='End', shape='ellipse'))
    if not flow or flow[-1][0] != 'return':
        graph.add_edge(pydot.Edge(prev_node, 'end'))

    return graph

# Utility function to generate unique filenames and handle file paths
def safe_write_png(graph, output_dir, file_name):
    try:
        output_path = os.path.join(output_dir, file_name)
        graph.write_png(output_path)
        print(f"Generated: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error writing {output_path}: {str(e)}")
        return None

# Main process function for file handling, class diagram, and flowchart generation
def process_file(file_path, language, author, doc_id):
    if language.lower() != 'java':
        return None  # If not Java, exit early
    
    # Analyze Java file for classes and methods
    classes, methods = analyze_java_file(file_path)

    if not classes:
        return None

    # Create output directory based on the author
    output_dir = os.path.join('uploads', author)
    os.makedirs(output_dir, exist_ok=True)

    # Generate class diagram and save it
    class_diagram_graph = generate_class_diagram({os.path.basename(file_path): classes})
    class_file_name = f"{os.path.basename(file_path)}_class_diagram_{doc_id}.png"
    class_diagram_path = safe_write_png(class_diagram_graph, output_dir, class_file_name)

    # Generate flowcharts for each method and save them
    for method_name, flow in methods.items():
        flowchart_graph = generate_flowchart(method_name, flow)
        flowchart_file_name = f"{os.path.basename(file_path)}_flowchart_{method_name}_{doc_id}.png"
        safe_write_png(flowchart_graph, output_dir, flowchart_file_name)

    return class_diagram_path  # Returning class diagram path for further processing

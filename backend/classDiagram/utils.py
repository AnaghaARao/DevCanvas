import os
import javalang
import pydot


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

def generate_java_class_diagram(all_classes):
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

def generate_flowchart(method_name, flow):
    graph = pydot.Dot(graph_type='digraph')
    graph.set_rankdir('TB')
    graph.set_size('12,12')
    
    graph.add_node(pydot.Node('start', label='Start', shape='ellipse'))
    prev_node = 'start'
    stack = []  # Stack to handle nested structures

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

def safe_write_png(graph, filename):
    try:
        graph.write_png(filename)
        print(f"Generated: {filename}")
    except Exception as e:
        print(f"Error writing {filename}: {str(e)}")
        print(f"Make sure you have write permissions in the output directory")

def process_file(file_path, language):
    if language.lower() == 'java':
        classes, methods = analyze_java_file(file_path)
        if classes:
            # Generate class diagram
            class_diagram = generate_java_class_diagram({os.path.basename(file_path): classes})
            class_output_path = 'Java_class_diagram.png'
            safe_write_png(class_diagram, class_output_path)
        
        if methods:
            # Generate flowcharts for each method
            for method_name, flow in methods.items():
                chart = generate_flowchart(method_name, flow)
                chart_output_path = f'Java_flowchart_{method_name}.png'
                safe_write_png(chart, chart_output_path)
                
        return class_output_path  # Return the path of the generated class diagram
    else:
        print(f"Unsupported language: {language}")
        return None

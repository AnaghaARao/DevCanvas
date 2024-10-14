import os
import pydot
import javalang

class JavaDiagramGenerator:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.classes = {}
        self.methods = {}

    def analyze_java_file(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            content = file.read()

            try:
                tree = javalang.parse.parse(content)
            except javalang.parser.JavaSyntaxError as e:
                return{
                    'error': f"Syntax error in file: {self.file_path}",
                    'details': str(e)
                }, None
            
            #continue with parsing logic if no syntax error occurs
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
                    methods[f"{class_name}.{method.name}"] = self.analyze_method_flow(method)

            return classes, methods
        
    # called by analyze_java_file; analyzes the file, determines the method flow
    def analyze_method_flow(self, method):
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
    
    # generates the class diagram and returns the graph
    def generate_class_diagram(self):
        graph = pydot.Dot(graph_type='digraph')
        graph.set_rankdir('TB')
        graph.set_size('12,12')

        for class_name, class_info in self.classes.items():
            methods = class_info['methods']
            method_str = '\\n'.join(methods)
            node = pydot.Node(class_name, label=f'{{{class_name}|{method_str}}}', shape='record')
            graph.add_node(node)

        for class_name, class_info in self.classes.items():
            if class_info['base_class']:
                edge = pydot.Edge(class_info['base_class'], class_name, label='extends')
                graph.add_edge(edge)

        return graph
    
    # based on the analyzed flow, the flowchart is generated
    def generate_flowchart(self, method_name, flow):
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
    
    # creates and saves the diagrams in predetermined location/dir
    def save_diagrams(self, output_dir):
        os.makedirs(output_dir, exist_ok=True)

        # Save class diagram
        class_diagram = self.generate_class_diagram()
        class_diagram_path = os.path.join(output_dir, f'{self.file_name}_class_diagram.png')
        class_diagram.write_png(class_diagram_path)

        # Save flowcharts for methods
        flowchart_paths = {}
        for method_name, flow in self.methods.items():
            flowchart = self.generate_flowchart(method_name, flow)
            flowchart_path = os.path.join(output_dir, f'{self.file_name}_{method_name}_flowchart.png')
            flowchart.write_png(flowchart_path)
            flowchart_paths[method_name] = flowchart_path

        # Return both class diagram and flowchart paths
        return class_diagram_path, flowchart_paths
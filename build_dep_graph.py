import json
import networkx as nx

def build_graph_from_json(file_path: str = 'deps.json') -> nx.DiGraph:
    with open('deps.json') as f:
        deps = json.load(f)
    
        nodes = []
        edges = []
    
        for _, value in deps.items():
            path = value['path']
            if is_valid_file(path):
                nodes.append(path)
        
            for imp in get_imports(value):
                edges.append((deps[imp]['path'], path))

        return build_graph_from_nodes_and_edges(nodes, edges)

def build_graph_from_nodes_and_edges(nodes: list[str], edges: list[tuple[str, str]]) -> nx.DiGraph:
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return G

def get_imports(value: dict) -> list:
    return value.get('imports', [])

def is_valid_file(path: str) -> bool:
    return "__init__.py" not in path

def save_graph(G, file_path: str = "deps.gml"):
    nx.write_gml(G, file_path)


print(build_graph_from_json().edges)
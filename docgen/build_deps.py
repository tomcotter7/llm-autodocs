import argparse
import json
import networkx as nx

from pathlib import Path

def build_graph_from_json(file_path: str | Path) -> nx.DiGraph:
    with open(file_path) as f:
        deps = json.load(f)
    
        nodes = []
        edges = []
    
        for _, value in deps.items():
            path = value['path']
            if is_documentable_file(path):
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

def is_documentable_file(path: str) -> bool:
    return "__init__.py" not in path

def save_graph(G, save_folder: str):
    nx.write_gml(G, Path(save_folder, "dep_graph.gml"))

# build and save graph
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_path', type=str)
    parser.add_argument('--save_path', type=str)
    args = parser.parse_args()
    save_graph(build_graph_from_json(args.file_path), args.save_path)

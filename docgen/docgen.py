"""Generate docstring for an entire python package"""
import argparse
import logging
import networkx as nx
import os
import re

from pathlib import Path

from docgen.dependencies import build_graph_from_json
from docgen.modules import generate_docstrings_for_module

def file_path_to_module_name(file_path: str, package_name: str) -> str:
    
    file_path = re.sub(r".*(" + package_name + r".*)\.py", r"\1", file_path)
    return file_path.replace(os.sep, ".")   


def docgen_module(module_file_path: str, package_name: str, imported_modules: list, function_visited: dict) -> dict:
    """Generate docstring for a single python module"""
    module_name = file_path_to_module_name(module_file_path, package_name)
    logging.info(f"Generating docstrings for module {module_name}")

    with open(module_file_path, "r") as f:
        source_code = f.read()

    new_source_code, new_visited = generate_docstrings_for_module(source_code, imported_modules, function_visited, module_name)

    logging.info(f"Writing updated source code to {module_name}")
    with open(module_file_path, "w") as f:
        f.write(new_source_code)

    return new_visited


def docgen(G: nx.DiGraph, package_name: str) -> None:
    """Generate docstring for an entire python package"""
    queue = [node for node in G.nodes if G.in_degree(node) == 0]
    function_visited = {}
    module_visited = set()
    while queue:
        node = queue.pop(0)
        parents = list(G.predecessors(node))
        function_visited = docgen_module(node, package_name, parents, function_visited)
        module_visited.add(node)
        queue.extend([n for n in G.successors(node) if n not in module_visited])


def main(dependencies_file: str, package_name: str) -> None:
    """Generate docstring for an entire python package"""
    logging.basicConfig(level=logging.INFO, encoding="utf-8")
    G = build_graph_from_json(dependencies_file)
    docgen(G, package_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate docstring for an entire python package")
    parser.add_argument("--dependencies_file", "-d", help="The file containing the dependencies of the package.")
    parser.add_argument("--package_name", "-p", help="The name of the package.")
    args = parser.parse_args()
    main(args.dependencies_file, args.package_name)


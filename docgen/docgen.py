import ast
import logging
import re

from docgen.docstring_utils import build_docstring, add_indentation
from docgen.build_deps import build_graph_from_json
from docgen.code_parsing import get_start_of_second_line_index, get_current_docstring, remove_current_docstring
from docgen.llm import generate_docstring
from docgen.pydantic_models import DocString

def get_used_functions(
        function_code: str,
        current_module: str,
        imports: list[str],
        visited: dict,
        aliases: dict
) -> list[tuple[str, str]]:

    used_functions = []
    
    imports.append(current_module)

    for import_name in imports:
        functions = visited.get(import_name, {})
        for func_name, ds_obj in functions.items():
            func_name = aliases.get(func_name, func_name)
            if func_name in function_code:
                docstring = ds_obj.summary
                used_functions.append((func_name, docstring))
    
    return used_functions

def get_docstring_for_function(
    function_code: str,
    current_module: str,
    imports: list[str],
    visited: dict,
    aliases: dict
) -> tuple[str, DocString]:

    current_docstring = get_current_docstring(function_code)

    if len(current_docstring) > 0:
        fn = re.search(r'def\s+(\w+)', function_code).group(1) # type: ignore
        logging.info(f"Docstring already exists for {fn}. Default is to remove and replace with AI generated docstring.")
        function_code = remove_current_docstring(function_code, current_docstring)
    
    functions_used_in_code = get_used_functions(function_code, current_module, imports, visited, aliases)
    docstring_object = generate_docstring(function_code, functions_used_in_code)
    docstring = build_docstring(docstring_object)
    docstring = add_indentation(docstring, function_code)
    
    eol = get_start_of_second_line_index(function_code) - 1
    new_function_code = function_code[:eol] + '\n' + docstring + function_code[eol:]
    
    
    return new_function_code, docstring_object
   
def get_docstrings_for_module(module: str, imports: list[str], visited: dict) -> dict:
    
    with open(module) as f:
        source_code = f.read()
    new_source_code = source_code
    
    aliases = {}
    tree = ast.parse(source_code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_code = ast.get_source_segment(source_code, node).strip() # type: ignore
            new_function_code, docstring_object = get_docstring_for_function(
                function_code,
                module,
                imports,
                visited,
                aliases
            )
            new_source_code = new_source_code.replace(function_code, new_function_code)
            visited = update_visited(visited, module, docstring_object)
            logging.info(f"Added docstring for {docstring_object.function_name}")
    
    logging.info(f"Updating {module}")
    update_module_with_docstrings(module, new_source_code)
        
    return visited

def update_visited(current_visited: dict, module: str, docstring_object: DocString)-> dict:

    
    if module not in current_visited:
        current_visited[module] = {}
    
    current_visited[module][docstring_object.function_name] = docstring_object
    return current_visited

def update_module_with_docstrings(module: str, new_source_code: str):
    with open(module, 'w') as f:
        f.write(new_source_code)

def docgen(file_path: str):
    
    G = build_graph_from_json(file_path)
    
    queue = [node for node in G.nodes if G.in_degree(node) == 0]
    visited = {}
    while queue:
        node = queue.pop(0)
        logging.info(f"Working on {node}")
        if node not in visited:
            parents = list(G.predecessors(node))
            visited = get_docstrings_for_module(node, parents, visited)
            queue.extend([n for n in G.successors(node)])
        

import ast
import re
from llm import get_docstring
from build_dep_graph import build_graph_from_json

def get_first_line_pos(function_code: str) -> int:
    definition = function_code.find('def')
    eol = function_code[definition:].find('\n')
    return eol + 1

def get_used_functions(function_code: str, imports: list[str], visited: dict) -> list[tuple[str, str]]:
    used_functions = []
    for import_name in imports:
        functions = visited.get(import_name, {})
        for function, details in functions.items():
            if function in function_code:
                docstring = details[1]
                used_functions.append((function, docstring))
    
    return used_functions

def get_current_docstring(function_code: str) -> str:
    eol = get_first_line_pos(function_code)
    current_docstring = [(m.start(0), m.end(0)) for m in re.finditer('"""', function_code)]
    if len(current_docstring) > 0:
        return function_code[eol+1:current_docstring[-1][1]]
    return "" 

def produce_docstring_for_function(
    function_code: str, imports: list[str],
    visited: dict, replace_existing_docstring: bool=False
) -> tuple[str, str]:
    current_docstring = get_current_docstring(function_code)
    if len(current_docstring) > 0:
        if not replace_existing_docstring:
            return function_code, current_docstring
            
        function_code = function_code.replace(current_docstring, '')
    
    functions_used_in_code = get_used_functions(function_code, imports, visited)
    docstring = add_indentation(get_docstring(function_code, functions_used_in_code))
    
    eol = get_first_line_pos(function_code) - 1
    new_function_code = function_code[:eol] + '\n' + docstring + function_code[eol:]
    
    
    return new_function_code, docstring

def add_indentation(docstring: str) -> str:
    indentation = calculate_indentation(docstring)
    if '"""' not in docstring:
        docstring = indentation + f'"""\n{docstring}\n"""'
    else:
        docstring = indentation + docstring
    docstring = docstring.replace('\n', '\n' + indentation).rstrip()
    return docstring

def calculate_indentation(function_code: str) -> str:
    first_line = function_code[get_first_line_pos(function_code):]
    first_non_whitespace = re.search('\S', first_line).start(0)
    indentation = first_line[:first_non_whitespace]
    return indentation
    
def get_docstrings_for_module(module: str, imports: list[str], visited: dict) -> dict:
    
    with open(module) as f:
        source_code = f.read()
    new_source_code = source_code
    
    tree = ast.parse(source_code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_code = ast.get_source_segment(source_code, node).strip()
            new_function_code, docstring = produce_docstring_for_function(
                function_code,
                imports,
                visited
            )
            new_source_code = new_source_code.replace(function_code, new_function_code)
            visited = update_visited(visited, module, node.name, new_function_code, docstring)
    
    update_module_with_docstrings(module, new_source_code)
        
    return visited

def update_visited(current_visited: dict, module: str, function_name: str,
                new_function_code: str, docstring: str) -> dict:
    
    if module not in current_visited:
        current_visited[module] = {}
    
    current_visited[module][function_name] = (new_function_code, docstring)
    return current_visited

def update_module_with_docstrings(module: str, new_source_code: str):
    with open(module, 'w') as f:
        f.write(new_source_code)

def main():
    
    G = build_graph_from_json()
    
    queue = [node for node in G.nodes if G.in_degree(node) == 0]
    visited = {}
    while queue:
        node = queue.pop(0)
        print(f"Working on {node}")
        if node not in visited:
            parents = list(G.predecessors(node))
            visited = get_docstrings_for_module(node, parents, visited)
            queue.extend([n for n in G.successors(node)])
        
    
if __name__ == '__main__':
    main()
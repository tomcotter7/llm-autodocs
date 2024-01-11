import ast
import re
from typing import Optional
from llm import generate_docstring
from build_dep_graph import build_graph_from_json
from pydantic_models import DocString

def build_docstring(docstring_object: DocString) -> str:
    init_docstring = f'"""{docstring_object.summary}\n\n{docstring_object.description}\n\n'


    def add_string(docstring: str, title: str, content: Optional[str]) -> str:
        if not content:
            return docstring
        docstring += f"{title}:\n\t{content}\n"
        return docstring

    def add_list(docstring: str, title: str, content: Optional[list[str]]) -> str:
        if not content:
            return docstring
        docstring += f"{title}:\n"
        for item in content:
            docstring += f"\t{item}\n"
        return docstring
    
    init_docstring = add_list(init_docstring, "Args", docstring_object.parameters)
    init_docstring = add_string(init_docstring, "Returns", docstring_object.returns)
    init_docstring = add_list(init_docstring, "Raises", docstring_object.raises)
    init_docstring = add_string(
            init_docstring,
            "Example",
            docstring_object.example.replace("\n", "\n\t") if docstring_object.example else None
    )
    init_docstring = add_string(init_docstring, "Yields", docstring_object.yields)

    init_docstring += '"""'

    return init_docstring

def get_first_line_pos(function_code: str) -> int:
    definition = function_code.find('def')
    eol = function_code[definition:].find('\n')
    return eol + 1

def get_used_functions(function_code: str, imports: list[str], visited: dict) -> list[tuple[str, str]]:
    used_functions = []
    for import_name in imports:
        functions = visited.get(import_name, {})
        for func_name, ds_obj in functions.items():
            if func_name in function_code:
                print(ds_obj.__fields__)
                docstring = ds_obj.summary
                used_functions.append((func_name, docstring))
    
    return used_functions

def get_current_docstring(function_code: str) -> str:
    eol = get_first_line_pos(function_code)
    current_docstring = [(m.start(0), m.end(0)) for m in re.finditer('"""', function_code)]
    if len(current_docstring) > 0:
        return function_code[eol+1:current_docstring[-1][1]]
    return "" 

def produce_docstring_for_function(
    function_code: str, imports: list[str],
    visited: dict 
) -> tuple[str, DocString]:
    current_docstring = get_current_docstring(function_code)
    if len(current_docstring) > 0:           
        function_code = function_code.replace(current_docstring, '')
    
    functions_used_in_code = get_used_functions(function_code, imports, visited)
    docstring_object = generate_docstring(function_code, functions_used_in_code)
    docstring = build_docstring(docstring_object)
    docstring = add_indentation(docstring, function_code)
    
    eol = get_first_line_pos(function_code) - 1
    new_function_code = function_code[:eol] + '\n' + docstring + function_code[eol:]
    
    
    return new_function_code, docstring_object

def add_indentation(docstring: str, function_code: str) -> str:
    indentation = calculate_indentation(function_code)
    if '"""' not in docstring:
        docstring = indentation + f'"""\n{docstring}\n"""'
    else:
        docstring = indentation + docstring
    docstring = docstring.replace('\n', '\n' + indentation).rstrip()
    return docstring

def calculate_indentation(function_code: str) -> str:
    first_line = function_code[get_first_line_pos(function_code):]
    first_non_whitespace = re.search(r'\S', first_line).start(0) # type: ignore
    indentation = first_line[:first_non_whitespace]
    return indentation
    
def get_docstrings_for_module(module: str, imports: list[str], visited: dict) -> dict:
    
    with open(module) as f:
        source_code = f.read()
    new_source_code = source_code
    
    tree = ast.parse(source_code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_code = ast.get_source_segment(source_code, node).strip() # type: ignore
            new_function_code, docstring_object = produce_docstring_for_function(
                function_code,
                imports,
                visited
            )
            new_source_code = new_source_code.replace(function_code, new_function_code)
            visited = update_visited(visited, module, docstring_object)
    
    update_module_with_docstrings(module, new_source_code)
        
    return visited

def update_visited(current_visited: dict, module: str, docstring_object: DocString)-> dict:
    
    if module not in current_visited:
        current_visited[module] = {}
    
    current_visited[module][docstring_object.function_name] = DocString
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
            print(visited)
            queue.extend([n for n in G.successors(node)])
        
    
if __name__ == '__main__':
    main()

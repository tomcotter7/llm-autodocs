"""This module contains functions for handling entire modules"""
import ast
import logging
import re

from docgen.docstrings import build_function_docstring_from_object, build_module_docstring_from_object
from docgen.exceptions import InternalFunctionCalledError, FunctionNotFound
from docgen.functions import generate_docstring_for_function, add_docstring_to_function, remove_current_docstring_from_source_code
from docgen.imports import get_module_imports
from docgen.llm import generate_module_docstring

def generate_docstrings_for_all_functions(
        module_source_code: str,
        fq_module_name: str,
        imported_functions: dict[str, str],
        internal_functions: list[tuple[str, ast.FunctionDef]],
        visited: dict[str, str]
) -> tuple[str, dict]:
    """Generate docstrings for all functions in the module

    Returns:
        tuple[str, dict, list]: The source code with docstrings added, a dictionary of visited functions, and a list of functions used in the module
    """
    new_source_code = module_source_code
    while internal_functions:
        name, function_obj = internal_functions.pop(0)
        logging.info(f"Generating docstring for function {name}")
        try:
            docstring_obj = generate_docstring_for_function(function_obj, internal_functions, imported_functions, visited)
        except InternalFunctionCalledError:
            logging.info(f"Moving function {name} to end of queue because it calls an internal function")
            internal_functions.append((name, function_obj))
            continue

        func_name = fq_module_name + '.' + name
        visited[func_name] = docstring_obj.summary

        docstring = build_function_docstring_from_object(docstring_obj)
        func_code = ast.get_source_segment(module_source_code, function_obj)
        if func_code is not None:
            logging.info(f"Removing existing docstring for {func_name}")
            updated_func_code = remove_current_docstring_from_source_code(func_code)
            updated_func_code = add_docstring_to_function(updated_func_code, docstring)
            logging.info(f"Updating source code for function {name}")
            new_source_code = new_source_code.replace(func_code, updated_func_code)
        else:
            raise FunctionNotFound("Unable to find source code for function")
    new_source_code = new_source_code.rstrip() + "\n"
    return new_source_code, visited

def get_all_internal_functions(module: ast.Module) -> list[tuple[str, ast.FunctionDef]]:
    """Get all functions in the module"""
    return [(node.name, node) for node in ast.walk(module) if isinstance(node, ast.FunctionDef)]
    

def add_top_level_docstring(
        source_code: str,
        module: ast.Module,
        functions_in_module: list[tuple[str, str]],
        module_name: str
) -> str: 
    """Generate a top level docstring for the module"""
    if_name_main = find_if_name_main(source_code)
    docstring_obj = generate_module_docstring(module_name, functions_in_module, if_name_main)
    docstring = build_module_docstring_from_object(docstring_obj)

    current_docstring = ast.get_docstring(module)
    if current_docstring:
        source_code = source_code.replace(current_docstring, docstring)
    else:
        source_code = '"""' + docstring + '"""\n' + source_code

    return source_code

def find_if_name_main(source_code: str) -> str|None:
    pattern = re.compile(r'if __name__ == "__main__":\n\s+((.|\n)*)')
    match = pattern.search(source_code)
    if match:
        return match.group(1).strip()
    return None


def generate_docstrings_for_module(
        source_code: str,
        imported_modules: list,
        visited: dict,
        module_name: str
) -> tuple[str, dict]:
    """Generate docstrings for the module"""
    tree = ast.parse(source_code)
    package_name = ".".join(module_name.split(".")[:-1])
    internal_functions = get_all_internal_functions(tree)
    imported_functions = get_module_imports(tree, set(imported_modules), package_name)
    old_visited = set(visited.keys())
    new_source_code, visited = generate_docstrings_for_all_functions(source_code, module_name, imported_functions, internal_functions, visited)
    logging.info(f"Generated functional docstrings for module {module_name}")
    new_functions = [(key, visited[key]) for key in (set(visited.keys()) - old_visited)]
    new_source_code = add_top_level_docstring(new_source_code, ast.parse(new_source_code), new_functions, module_name)
    return new_source_code, visited

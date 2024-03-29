"""This module contains functions for handling entire functions"""
import ast
import logging
import re

from docgen.exceptions import InternalFunctionCalledError
from docgen.docstrings import calculate_indentation, add_indentation
from docgen.llm import generate_function_docstring
from docgen.pydantic_models import FunctionDocstring

def get_function_name(function: ast.FunctionDef) -> str:
    """Returns the name of the function"""
    return function.name

def handle_call(
        call: ast.Call,
        internal_functions: list[str],
        imported_functions: dict,
        visited: dict
) -> tuple:
    """Return the summary of the function called if the LLM has previously seen it.

    Args:
        call: The call AST object.
        internal_functions: The list of other functions in the module.
        imported_functions: The dictionary of imported functions from other modules in the package.
        visited: The dictionary of visited functions.

    Returns:
        The name of the function called and its summary. An empty tuple if the function has not been visited.

    Raises:
        InternalFunctionCalledError: If the function calls another function in the module which has not yet been visited.
    """

    if isinstance(call.func, ast.Name) and call.func.id in imported_functions.keys():

        try:
            return (call.func.id, visited[imported_functions[call.func.id]])
        except KeyError:
            return ()
    
    elif isinstance(call.func, ast.Name) and call.func.id in internal_functions:

        raise InternalFunctionCalledError
    
    elif isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Constant):
        return ()

    elif isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Call):
        return handle_call(call.func.value, internal_functions, imported_functions, visited)

    elif isinstance(call.func, ast.Attribute) and call.func.value.id in imported_functions.keys(): # type: ignore
        fq_name = imported_functions[call.func.value.id] + '.' + call.func.attr # type: ignore
        try:
            return (call.func.value.id + '.' + call.func.attr, visited[fq_name]) # type: ignore
        except KeyError:
            return ()

    return ()



def get_used_functions(
        function: ast.FunctionDef,
        internal_functions: list[str],
        imported_functions: dict,
        visited: dict
) -> list:
    """Return a list of the functions used in the function with respect to the imported functions

    Args:
        function: The function AST object.
        internal_functions: The list of other functions called in the module that are not yet visited.
        imported_functions: The dictionary of imported functions from other modules in the package.
        visited: The dictionary of visited functions.

    Returns:
        A list of tuples containing the name of the function and its summary.

    Raises:
        InternalFunctionCalledError: If the function calls another function in the module which has not yet been visited.
    """

    used_functions = []
    
    for node in ast.walk(function):
        if isinstance(node, ast.Call):
            call_summary = handle_call(node, internal_functions, imported_functions, visited)
            if call_summary:
                used_functions.append(call_summary)

                    
    return used_functions

def generate_docstring_for_function(
        function: ast.FunctionDef,
        internal_functions: list[tuple[str, ast.FunctionDef]],
        imported_functions: dict,
        visited: dict
) -> FunctionDocstring:
    """Generate a docstring for the function

    Preprocesses the function by collecting all the functions used within it, removes the existing docstring, and then generates a new docstring.

    Args:
        function: The function AST object.
        internal_functions: The list of other functions called in the module that are not yet visited.
        imported_functions: The dictionary of imported functions from other modules in the package.
        visited: The dictionary of visited functions.

    Returns:
        A FunctionDocstring object which contains the information required to build a docstring.

    Raises:
        InternalFunctionCalledError: If the function calls another function in the module which has not yet been visited.
    """
    logging.info(f"Obtaining used functions for {function.name}")
    used_functions = get_used_functions(function, [name for name, _ in internal_functions], imported_functions, visited)
    
    # default is to just remove any existing docstring. TODO: parameterize this.
    if get_current_docstring(function):
        function = remove_current_docstring(function)

    function_code = ast.unparse(function)

    docstring = generate_function_docstring(
        function_code,
        used_functions
    )

    return docstring


def get_current_docstring(
        function: ast.FunctionDef
) -> str | None:
    """Get the current docstring for the function.

    Args:
        function: The function AST object.

    Returns:
        The current docstring for the function. None if there is no docstring.
    """
    return ast.get_docstring(function)

def remove_current_docstring(function: ast.FunctionDef) -> ast.FunctionDef:
    """Remove the current docstring from a ast.FunctionDef object.

    Args:
        function: The function AST object.
    
    Returns:
        The function AST object without the docstring.
    """
    function.body = function.body[1:]
    return function

def remove_current_docstring_from_source_code(
        function_code: str
) -> str:
    """Remove the current docstring from the source code of a function.

    Args:
        function_code: The source code of the function.

    Returns:
        The source code of the function without the docstring.
    """
    function_code = re.sub(r'\n\s+\"\"\"(.|\n)*\"\"\"', '', function_code)
    return function_code

def add_docstring_to_function(
        function_code: str,
        docstring: str
) -> str:
    """Add a docstring to the function source code.

    Args:
        function_code: The source code of the function.
        docstring: The docstring to add to the function.

    Returns:
        The source code of the function with the docstring added.
    """
    indentation = calculate_indentation(function_code)
    docstring = add_indentation('"""' + docstring + '"""', indentation)
    function_code_split = function_code.strip().split("\n")
    function_code_split.insert(1, docstring)
    function_code = "\n".join(function_code_split)
    return function_code


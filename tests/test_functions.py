import ast
import pytest

from docgen.exceptions import InternalFunctionCalledError
from docgen.functions import (
    get_function_name,
    get_used_functions,
    get_current_docstring,
    remove_current_docstring,
    add_docstring_to_function,
    handle_call
)


def test_get_function_name():
    
    tree = ast.parse("def foo():\n\tpass")
    fn = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            fn = get_function_name(node)

    assert fn == "foo"

def test_get_function_name_with_args():
    
    tree = ast.parse("def foo(a, b):\n\tpass")
    fn = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            fn = get_function_name(node)

    assert fn == "foo"

def test_get_used_functions_no_imports():
    
    tree = ast.parse("def foo():\n\tbar()\n")
    used_functions = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            used_functions = get_used_functions(node, [], {}, {})
    
    assert used_functions == []

def test_get_used_functions_with_imports():

    tree = ast.parse("def foo():\n\tbar()\n")
    used_functions = None

    imported_functions = {'bar': 'package.foo.bar'}
    visited = {'package.foo.bar': 'This is the summary of bar'}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            used_functions = get_used_functions(node, [], imported_functions, visited)

    assert used_functions == [('bar', 'This is the summary of bar')]

def test_get_used_functions_with_imports_imported_function_not_in_visited():

    tree = ast.parse("def foo():\n\tbar()\n")
    used_functions = None

    imported_functions = {'bar': 'package.foo.bar'}
    visited = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            used_functions = get_used_functions(node, [], imported_functions, visited)

    assert used_functions == []

def test_get_used_functions_module_import():

    tree = ast.parse("def foo():\n\tbar.baz()\n")
    used_functions = None
    imported_functions = {'bar': 'package.bar'}
    visited = {'package.bar.baz': 'This is the summary of baz'}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            used_functions = get_used_functions(node, [], imported_functions, visited)

    assert used_functions == [('bar.baz', 'This is the summary of baz')]

def test_get_used_functions_module_import_not_in_visited():

    tree = ast.parse("def foo():\n\tbar.baz()\n")
    used_functions = None
    imported_functions = {'bar': 'package.bar'}
    visited = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            used_functions = get_used_functions(node, [], imported_functions, visited)

    assert used_functions == []

def test_get_used_functions_multiple_functions_function_import():
    
    tree = ast.parse("def foo():\n\tbar()\n\tbaz()\n")
    used_functions = None
    imported_functions = {'bar': 'package.foo.bar', 'baz': 'package.foo.baz'}
    visited = {'package.foo.bar': 'This is the summary of bar', 'package.foo.baz': 'This is the summary of baz'}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            used_functions = get_used_functions(node, [], imported_functions, visited)

    assert used_functions == [('bar', 'This is the summary of bar'), ('baz', 'This is the summary of baz')]


def test_get_used_functions_multiple_functions_module_import():

    tree = ast.parse("def foo():\n\tbar.baz()\n\tbar.qux()\n")
    used_functions = None
    imported_functions = {'bar': 'package.bar'}
    visited = {'package.bar.baz': 'This is the summary of baz', 'package.bar.qux': 'This is the summary of qux'}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            used_functions = get_used_functions(node, [], imported_functions, visited)

    assert used_functions == [('bar.baz', 'This is the summary of baz'), ('bar.qux', 'This is the summary of qux')]

def test_get_used_functions_multiple_functions_mixed_imports():

    tree = ast.parse("def foo():\n\tbaz()\n\tbar.qux()\n")
    used_functions = None
    imported_functions = {'baz': 'package.foo.baz', 'bar': 'package.bar'}
    visited = {'package.foo.baz': 'This is the summary of baz', 'package.bar.qux': 'This is the summary of qux'}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            used_functions = get_used_functions(node, [], imported_functions, visited)

    assert used_functions == [('baz', 'This is the summary of baz'), ('bar.qux', 'This is the summary of qux')]

def test_handle_call_raises_exception_with_internal_function():

    tree = ast.parse("def foo():\n\tbar()\n")
    internal_functions = ["bar"]
    imported_functions = {}
    visited = {}

    with pytest.raises(InternalFunctionCalledError):
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                handle_call(node, internal_functions, imported_functions, visited)

def test_get_current_docstring_no_docstring():

    tree = ast.parse("def foo():\n\tbar()\n")
    docstring = ''
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            docstring = get_current_docstring(node)

    assert docstring is None

def test_get_current_docstring_with_docstring():

    tree = ast.parse('def foo():\n\t"""This is the docstring"""\n\tbar()\n')
    docstring = ''
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            docstring = get_current_docstring(node)

    assert docstring == 'This is the docstring'

def test_remove_docstring():

    tree = ast.parse('def foo():\n\t"""This is the docstring"""\n\tbar()\n')
    node = None
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            node = remove_current_docstring(node)
            break

    assert ast.get_docstring(node) is None and ast.unparse(node) == 'def foo():\n    bar()' # type: ignore

def test_add_docstring_to_function():
    code = 'def foo():\n\tbar()\n'
    tree = ast.parse(code)
    func_code = ""
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_code = ast.get_source_segment(code, node)
            if func_code is not None:
                func_code = add_docstring_to_function(func_code, 'This is the docstring')
                break
    
    assert func_code == 'def foo():\n\t"""This is the docstring"""\n\tbar()' # type: ignore


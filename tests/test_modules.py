import ast

from unittest.mock import patch

from docgen.exceptions import InternalFunctionCalledError
from docgen.modules import get_all_internal_functions, generate_docstrings_for_all_functions
from docgen.pydantic_models import DocString

def test_get_all_internal_functions():

    module = ast.parse("def foo():\n\tbar()\n\ndef baz():\n\tfoo()\n")

    functions = get_all_internal_functions(module)

    assert functions[0][0] == "foo"
    assert functions[1][0] == "baz"

@patch("docgen.modules.generate_docstring_for_function")
def test_generate_docstrings_for_all_functions_no_imports_no_internal_calls(mock_generate):

    mock_generate.return_value = DocString(function_name="foo", summary="This is the docstring for foo", description="This is the description for foo")
    
    source_code = "def foo():\n\tprint(\"Hello World\")\n"
    module = ast.parse(source_code)
    imported_functions = {}
    internal_functions = [(node.name, node) for node in ast.walk(module) if isinstance(node, ast.FunctionDef)]
    visited = {}
    
    updated_source_code, visited = generate_docstrings_for_all_functions(
            source_code,
            "package.foo",
            imported_functions,
            internal_functions,
            visited
    )
    expected_source_code = "def foo():\n\t\"\"\"This is the docstring for foo\n\n\tThis is the description for foo\n\t\"\"\"\n\tprint(\"Hello World\")\n"
    
    assert updated_source_code == expected_source_code
    assert visited == {"package.foo.foo": "This is the docstring for foo"}

@patch("docgen.modules.generate_docstring_for_function")
def test_generate_docstrings_for_all_functions_with_internal_calls(mock_generate):

    mock_generate.side_effect = [
        InternalFunctionCalledError,
        DocString(function_name="bar", summary="This is the docstring for bar", description="This is the description for bar"),
        DocString(function_name="foo", summary="This is the docstring for foo", description="This is the description for foo"),
    ]
    source_code = "def foo():\n\tbar()\n\ndef bar():\n\tprint(\"Hello World\")\n"
    internal_functions = [(node.name, node) for node in ast.walk(ast.parse(source_code)) if isinstance(node, ast.FunctionDef)]
    imported_functions = {}
    visited = {}

    _, visited = generate_docstrings_for_all_functions(
            source_code,
            "package.foo",
            imported_functions,
            internal_functions,
            visited
    )
    
    # should be call to generate foo, raise exception because bar is called internally, then call to bar, then call to generate foo again.
    assert mock_generate.call_count == 3
    assert mock_generate.call_args_list[2][0][0].name == "foo"

    assert visited['package.foo.foo'] == "This is the docstring for foo"
    assert visited['package.foo.bar'] == "This is the docstring for bar"







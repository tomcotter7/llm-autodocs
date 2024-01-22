import ast

from unittest.mock import patch

from docgen.exceptions import InternalFunctionCalledError
from docgen.modules import (
        get_all_internal_functions,
        generate_docstrings_for_all_functions,
        add_top_level_docstring,
        find_if_name_main
)
from docgen.pydantic_models import FunctionDocstring, ModuleDocstring

def test_get_all_internal_functions():

    module = ast.parse("def foo():\n\tbar()\n\ndef baz():\n\tfoo()\n")

    functions = get_all_internal_functions(module)

    assert functions[0][0] == "foo"
    assert functions[1][0] == "baz"

@patch("docgen.modules.generate_docstring_for_function")
def test_generate_docstrings_for_all_functions_no_imports_no_internal_calls(mock_generate):

    mock_generate.return_value = FunctionDocstring(function_name="foo", summary="This is the docstring for foo", description="This is the description for foo")
    
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
        FunctionDocstring(function_name="bar", summary="This is the docstring for bar", description="This is the description for bar"),
        FunctionDocstring(function_name="foo", summary="This is the docstring for foo", description="This is the description for foo"),
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

@patch("docgen.modules.generate_docstring_for_function")
@patch("docgen.modules.build_function_docstring_from_object")
@patch("docgen.modules.add_docstring_to_function")
def test_generate_docstrings_for_all_functions_no_existing_docstrings(mock_add, mock_build, mock_generate):

    mock_generate.side_effect = [
        FunctionDocstring(
            function_name="foo",
            summary="This is the docstring for foo",
            description="This is the description for foo"
        ),
        FunctionDocstring(
            function_name="bar",
            summary="This is the docstring for bar",
            description="This is the description for bar"
        ),
    ]

    mock_build.side_effect = ['"""This is the docstring for foo\n\nThis is the description for foo\n"""', '"""This is the docstring for bar\n\nThis is the description for bar\n"""']

    mock_add.side_effect = [
        'def foo():\n\t"""This is the docstring for foo\n\n\tThis is the description for foo\n\t"""\n\tprint(\"Hello World\")',
        'def bar():\n\t"""This is the docstring for bar\n\n\tThis is the description for bar\n\t"""\n\tprint(\"Hello World\")',
    ]

    source_code = "def foo():\n\tprint(\"Hello World\")\n\ndef bar():\n\tprint(\"Hello World\")\n"

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

    expected_source_code = 'def foo():\n\t"""This is the docstring for foo\n\n\tThis is the description for foo\n\t"""\n\tprint(\"Hello World\")\n\ndef bar():\n\t"""This is the docstring for bar\n\n\tThis is the description for bar\n\t"""\n\tprint(\"Hello World\")\n'

    assert updated_source_code == expected_source_code

@patch("docgen.modules.generate_docstring_for_function")
@patch("docgen.modules.build_function_docstring_from_object")
@patch("docgen.modules.add_docstring_to_function")
def test_generate_docstrings_for_all_functions_with_existing_docstrings(mock_add, mock_build, mock_generate):

    mock_generate.side_effect = [
        FunctionDocstring(
            function_name="foo",
            summary="This is the docstring for foo",
            description="This is the description for foo"
        ),
        FunctionDocstring(
            function_name="bar",
            summary="This is the docstring for bar",
            description="This is the description for bar"
        ),
    ]

    mock_build.side_effect = ['"""This is the docstring for foo\n\nThis is the description for foo\n"""', '"""This is the docstring for bar\n\nThis is the description for bar\n"""']

    mock_add.side_effect = [
        'def foo():\n\t"""This is the docstring for foo\n\n\tThis is the description for foo\n\t"""\n\tprint(\"Hello World\")',
        'def bar():\n\t"""This is the docstring for bar\n\n\tThis is the description for bar\n\t"""\n\tprint(\"Hello World\")',
    ]

    source_code = 'def foo():\n\t\"\"\"Old docstring\"\"\"\n\tprint(\"Hello World\")\n\ndef bar():\n\t\"\"\"Old docstring\"\"\"\n\tprint(\"Hello World\")\n'

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
    
    print([updated_source_code])

    expected_source_code = 'def foo():\n\t"""This is the docstring for foo\n\n\tThis is the description for foo\n\t"""\n\tprint(\"Hello World\")\n\ndef bar():\n\t"""This is the docstring for bar\n\n\tThis is the description for bar\n\t"""\n\tprint(\"Hello World\")\n'

    assert updated_source_code == expected_source_code


@patch("docgen.modules.generate_module_docstring")
@patch("docgen.modules.build_module_docstring_from_object")
def test_add_top_level_docstring_docstring_does_not_exist(mock_object, mock_generate):
    
    mock_generate.return_value = ModuleDocstring(summary="A module called foo")
    mock_object.return_value = "A module called foo"

    source_code = "print(\"Hello World\")\n"
    module = ast.parse(source_code)
    functions_in_module = []
    module_name = "foo"

    updated_source_code = add_top_level_docstring(source_code, module, functions_in_module, module_name)

    expected_source_code = '"""A module called foo"""\nprint(\"Hello World\")\n'

    assert updated_source_code == expected_source_code

@patch("docgen.modules.generate_module_docstring")
@patch("docgen.modules.build_module_docstring_from_object")
def test_add_top_level_docstring_docstring_exists(mock_object, mock_generate):

    mock_generate.return_value = ModuleDocstring(summary="A module called foo")
    mock_object.return_value = "A module called foo"

    source_code = '"""A module called bar"""\nprint(\"Hello World\")\n'
    module = ast.parse(source_code)
    functions_in_module = []
    module_name = "foo"

    updated_source_code = add_top_level_docstring(source_code, module, functions_in_module, module_name)

    expected_source_code = '"""A module called foo"""\nprint(\"Hello World\")\n'

    assert updated_source_code == expected_source_code

def test_find_if_name_main_no_if_name_main():

    source_code = "print(\"Hello World\")\n"
    name_main = find_if_name_main(source_code)

    assert name_main is None

def test_find_if_name_main():

    source_code = "if __name__ == \"__main__\":\n\tprint(\"Hello World\")\n"
    name_main = find_if_name_main(source_code)

    assert name_main == "print(\"Hello World\")\n"

from unittest.mock import patch

from docgen.pydantic_models import FunctionDocstring, ModuleDocstring
from docgen.docstrings import (
        build_function_docstring_from_object,
        calculate_indentation,
        add_indentation,
        build_module_docstring_from_object
)


def test_build_function_docstring_from_object_from_object_no_optional_attributes():
    docstring_object = FunctionDocstring(
        function_name="function",
        summary="This a is a docstring",
        description="This is a description",
    )
    docstring = build_function_docstring_from_object(docstring_object)
    expected_docstring = 'This a is a docstring\n\nThis is a description\n'
    assert docstring == expected_docstring


def test_build_function_docstring_from_object_from_object_parameters():
    docstring_object = FunctionDocstring(
        function_name="function",
        summary="This a is a docstring",
        description="This is a description",
        parameters=["x: param1", "y: param2"],
    )
    docstring = build_function_docstring_from_object(docstring_object)
    expected_docstring = 'This a is a docstring\n\nThis is a description\nArgs:\n\tx: param1\n\ty: param2\n'
    assert docstring == expected_docstring

def test_build_function_docstring_from_object_from_object_returns():
    docstring_object = FunctionDocstring(
        function_name="function",
        summary="This a is a docstring",
        description="This is a description",
        returns="int",
    )
    docstring = build_function_docstring_from_object(docstring_object)
    expected_docstring = 'This a is a docstring\n\nThis is a description\nReturns:\n\tint\n'
    assert docstring == expected_docstring

def test_build_function_docstring_from_object_from_object_raises():
    docstring_object = FunctionDocstring(
        function_name="function",
        summary="This a is a docstring",
        description="This is a description",
        raises=["ValueError", "TypeError"],
    )
    docstring = build_function_docstring_from_object(docstring_object)
    expected_docstring = 'This a is a docstring\n\nThis is a description\nRaises:\n\tValueError\n\tTypeError\n'
    assert docstring == expected_docstring

def test_build_function_docstring_from_object_from_object_example():
    docstring_object = FunctionDocstring(
        function_name="function",
        summary="This a is a docstring",
        description="This is a description",
        example="x = 1\ny = 2",
    )
    docstring = build_function_docstring_from_object(docstring_object)
    expected_docstring = 'This a is a docstring\n\nThis is a description\nExample:\n\tx = 1\n\ty = 2\n'
    assert docstring == expected_docstring

def test_build_function_docstring_from_object_from_object_yields():
    docstring_object = FunctionDocstring(
        function_name="function",
        summary="This a is a docstring",
        description="This is a description",
        yields="int",
    )
    docstring = build_function_docstring_from_object(docstring_object)
    expected_docstring = 'This a is a docstring\n\nThis is a description\nYields:\n\tint\n'
    assert docstring == expected_docstring

def test_build_function_docstring_from_object_all():
    docstring_object = FunctionDocstring(
        function_name="function",
        summary="This a is a docstring",
        description="This is a description",
        parameters=["x: param1", "y: param2"],
        returns="int",
        raises=["ValueError", "TypeError"],
        example="x = 1\ny = 2",
        yields="int"
    )
    docstring = build_function_docstring_from_object(docstring_object)
    expected_docstring = 'This a is a docstring\n\nThis is a description\nArgs:\n\tx: param1\n\ty: param2\nReturns:\n\tint\nRaises:\n\tValueError\n\tTypeError\nExample:\n\tx = 1\n\ty = 2\nYields:\n\tint\n'
    assert docstring == expected_docstring

def test_calculate_indentation_no_indent():

    function_code = "print(\"Hello World\")\nprint(\"Hello World\")\n"
    indentation = calculate_indentation(function_code)

    assert indentation == ""

def test_calculate_indentation_two_spaces():
    
    function_code = "def foo():\n  print(\"Hello World\")\n"
    indentation = calculate_indentation(function_code)

    assert indentation == "  "

def test_calculate_indentation_four_spaces():
    
    function_code = "def foo():\n    print(\"Hello World\")\n"
    indentation = calculate_indentation(function_code)

    assert indentation == "    "

def test_calculate_indentation_tab():

    function_code = "def foo():\n\tprint(\"Hello World\")\n"
    indentation = calculate_indentation(function_code)

    assert indentation == "\t"


def test_add_indentation_two_spaces():
    docstring = "This is a docstring\nThis is a description\n"
    indentation = "  "
    expected_docstring = "  This is a docstring\n  This is a description\n"
    docstring = add_indentation(docstring, indentation)
    assert docstring == expected_docstring

def test_add_indentation_four_spaces():
    docstring = "This is a docstring\nThis is a description\n"
    indentation = "    "
    expected_docstring = "    This is a docstring\n    This is a description\n"
    docstring = add_indentation(docstring, indentation)
    assert docstring == expected_docstring

def test_add_indentation_tab():
    docstring = "This is a docstring\nThis is a description\n"
    indentation = "\t"
    expected_docstring = "\tThis is a docstring\n\tThis is a description\n"
    docstring = add_indentation(docstring, indentation)
    assert docstring == expected_docstring

def test_add_indentation_dual_indent():

    docstring = "Args:\n\tx: param1\n\ty: param2\n"
    indentation = "\t"

    expected_docstring = "\tArgs:\n\t\tx: param1\n\t\ty: param2\n"
    docstring = add_indentation(docstring, indentation)
    assert docstring == expected_docstring

def test_build_module_docstring_from_object_only_summary():

    docstring_object = ModuleDocstring(
        summary="This is a module",
    )
    docstring = build_module_docstring_from_object(docstring_object)
    expected_docstring = "This is a module"
    assert docstring == expected_docstring

def test_build_module_docstring_from_object_summary_and_additional_info():

    docstring_object = ModuleDocstring(
        summary="This is a module",
        additional_info="This is additional information",
    )
    docstring = build_module_docstring_from_object(docstring_object)
    expected_docstring = "This is a module\n\nThis is additional information\n"
    assert docstring == expected_docstring

def test_build_module_docstring_from_object_summary_and_usage():

    docstring_object = ModuleDocstring(
        summary="This is a module",
        usage="This is how to use the module",
    )
    docstring = build_module_docstring_from_object(docstring_object)
    expected_docstring = "This is a module\n\nUsage:\n\tThis is how to use the module\n"
    assert docstring == expected_docstring


from unittest.mock import patch

from docgen.pydantic_models import DocString
from docgen.docstrings import build_docstring_from_object, calculate_indentation, add_indentation


def test_build_docstring_from_object_from_object_no_optional_attributes():
    docstring_object = DocString(
        function_name="function",
        summary="This a is a docstring",
        description="This is a description",
    )
    docstring = build_docstring_from_object(docstring_object)
    expected_docstring = 'This a is a docstring\n\nThis is a description\n'
    assert docstring == expected_docstring


def test_build_docstring_from_object_from_object_parameters():
    docstring_object = DocString(
        function_name="function",
        summary="This a is a docstring",
        description="This is a description",
        parameters=["x: param1", "y: param2"],
    )
    docstring = build_docstring_from_object(docstring_object)
    expected_docstring = 'This a is a docstring\n\nThis is a description\nArgs:\n\tx: param1\n\ty: param2\n'
    assert docstring == expected_docstring

def test_build_docstring_from_object_from_object_returns():
    docstring_object = DocString(
        function_name="function",
        summary="This a is a docstring",
        description="This is a description",
        returns="int",
    )
    docstring = build_docstring_from_object(docstring_object)
    expected_docstring = 'This a is a docstring\n\nThis is a description\nReturns:\n\tint\n'
    assert docstring == expected_docstring

def test_build_docstring_from_object_from_object_raises():
    docstring_object = DocString(
        function_name="function",
        summary="This a is a docstring",
        description="This is a description",
        raises=["ValueError", "TypeError"],
    )
    docstring = build_docstring_from_object(docstring_object)
    expected_docstring = 'This a is a docstring\n\nThis is a description\nRaises:\n\tValueError\n\tTypeError\n'
    assert docstring == expected_docstring

def test_build_docstring_from_object_from_object_example():
    docstring_object = DocString(
        function_name="function",
        summary="This a is a docstring",
        description="This is a description",
        example="x = 1\ny = 2",
    )
    docstring = build_docstring_from_object(docstring_object)
    expected_docstring = 'This a is a docstring\n\nThis is a description\nExample:\n\tx = 1\n\ty = 2\n'
    assert docstring == expected_docstring

def test_build_docstring_from_object_from_object_yields():
    docstring_object = DocString(
        function_name="function",
        summary="This a is a docstring",
        description="This is a description",
        yields="int",
    )
    docstring = build_docstring_from_object(docstring_object)
    expected_docstring = 'This a is a docstring\n\nThis is a description\nYields:\n\tint\n'
    assert docstring == expected_docstring

def test_build_docstring_from_object_all():
    docstring_object = DocString(
        function_name="function",
        summary="This a is a docstring",
        description="This is a description",
        parameters=["x: param1", "y: param2"],
        returns="int",
        raises=["ValueError", "TypeError"],
        example="x = 1\ny = 2",
        yields="int"
    )
    docstring = build_docstring_from_object(docstring_object)
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

from unittest.mock import patch

from docgen.docstring_utils import build_docstring, add_indentation

def test_add_indentation():
    docstring = '"""This a is a docstring\nArgs:\n\tx: param1\n"""'
    with patch("docgen.code_parsing.calculate_indentation") as mock:
        mock.return_value = "    "
        indented_docstring = add_indentation(docstring, "def function():\n    pass")
        expected_docstring = '    """This a is a docstring\n    Args:\n        x: param1\n    """'
        assert indented_docstring == expected_docstring

def test_add_indentation_double_newline():
    docstring = '"""This a is a docstring\n\nArgs:\n\tx: param1\n\n"""'
    with patch("docgen.code_parsing.calculate_indentation") as mock:
        mock.return_value = "    "
        indented_docstring = add_indentation(docstring, "def function():\n    pass")
        expected_docstring = '    """This a is a docstring\n\n    Args:\n        x: param1\n\n    """'
        assert indented_docstring == expected_docstring

def test_build_docstring():
    from docgen.pydantic_models import DocString
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
    docstring = build_docstring(docstring_object)
    expected_docstring = '"""This a is a docstring\n\nThis is a description\n\nArgs:\n\tx: param1\n\ty: param2\nReturns:\n\tint\nRaises:\n\tValueError\n\tTypeError\nExample:\n\tx = 1\n\ty = 2\nYields:\n\tint\n"""'
    assert docstring == expected_docstring

def test_build_docstring_missing_sections():
    from docgen.pydantic_models import DocString

    docstring_object = DocString(
        function_name="function",
        summary="This a is a docstring",
        description="This is a description",
        returns="the answer",
    )

    docstring = build_docstring(docstring_object)

    assert docstring == '"""This a is a docstring\n\nThis is a description\n\nReturns:\n\tthe answer\n"""'


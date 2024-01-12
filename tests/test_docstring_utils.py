from unittest.mock import patch

from docgen.docstring_utils import build_docstring, add_indentation


def test_add_indentation_four_spaces():
    docstring = '"""This a is a docstring\n\nArgs:\n\tx: param1\n\n"""'
    with patch("docgen.code_parsing.calculate_indentation") as mock:
        mock.return_value = "    "
        indented_docstring = add_indentation(docstring, "def function():\n    pass")
        assert indented_docstring == '    """This a is a docstring\n\n    Args:\n        x: param1\n\n    """'
        


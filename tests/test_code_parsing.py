from docgen.code_parsing import get_start_of_second_line_index, get_current_docstring, calculate_indentation, remove_current_docstring

def test_get_start_of_second_line_index():
    function_code = "def function():\n\tpass"
    sli = get_start_of_second_line_index(function_code)
    assert function_code[sli:] == "\tpass"

def test_get_start_of_second_line_with_newlines_before_def():
    function_code = "\n\ndef function():\n\tpass"
    sli = get_start_of_second_line_index(function_code)
    assert function_code[sli:] == "\tpass"

def test_get_current_docstring():
    function_code = "def function():\n\t\"\"\"This is a docstring\"\"\"\n\tpass"
    docstring = get_current_docstring(function_code)
    assert docstring == '"""This is a docstring"""\n\t'

def test_get_current_docstring_no_docstring():
    function_code = "def function():\n\tpass"
    docstring = get_current_docstring(function_code)
    assert docstring == ""


def test_calculate_indentation():
    function_code = "def function():\n\tpass"
    indentation = calculate_indentation(function_code)
    assert indentation == "\t"

def test_calculate_indentation_with_spaces():
    function_code = "def function():\n    pass"
    indentation = calculate_indentation(function_code)
    assert indentation == "    "

def test_remove_current_docstring():
    function_code = "def function():\n\t\"\"\"This is a docstring\"\"\"\n\tpass"
    current_docstring = '"""This is a docstring"""\n\t'
    new_function_code = remove_current_docstring(function_code, current_docstring)
    assert new_function_code == "def function():\n\tpass"

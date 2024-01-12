import re

def get_start_of_second_line_index(function_code: str) -> int:
    definition = function_code.find('def')
    eol = function_code[definition:].find('\n')
    return eol + definition + 1

def get_current_docstring(function_code: str) -> str:
    eol = get_start_of_second_line_index(function_code)
    current_docstring = [(m.start(0), m.end(0)) for m in re.finditer('"""', function_code)]
    if len(current_docstring) > 0:
        end_of_docstring = current_docstring[-1][1]
        first_non_whitespace = re.search(r'\S', function_code[end_of_docstring:]).start(0)
        return function_code[eol+1:current_docstring[-1][1] + first_non_whitespace]
    return "" 

def calculate_indentation(function_code: str) -> str:
    func_without_def = function_code[get_start_of_second_line_index(function_code):]
    first_non_whitespace = re.search(r'\S', func_without_def).start(0) # type: ignore
    indentation = func_without_def[:first_non_whitespace]
    return indentation

def remove_current_docstring(function_code: str, current_docstring: str) -> str:
    eol = get_start_of_second_line_index(function_code)
    return function_code[:eol] + function_code[eol:].replace(current_docstring, "")

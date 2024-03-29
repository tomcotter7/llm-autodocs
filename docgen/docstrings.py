import re

from typing import Optional

from docgen.pydantic_models import FunctionDocstring, ModuleDocstring

def add_string(docstring: str, title: str, content: Optional[str]) -> str:
    if not content:
        return docstring
    docstring += f"{title}:\n\t{content}\n"
    return docstring

def add_list(docstring: str, title: str, content: Optional[list[str]]) -> str:
    if not content:
        return docstring
    docstring += f"{title}:\n"
    for item in content:
        docstring += f"\t{item}\n"
    return docstring

def build_function_docstring_from_object(docstring_object: FunctionDocstring) -> str:
    init_docstring = f'{docstring_object.summary}\n\n{docstring_object.description}\n'

    
    init_docstring = add_list(init_docstring, "Args", docstring_object.parameters)
    init_docstring = add_string(init_docstring, "Returns", docstring_object.returns)
    init_docstring = add_list(init_docstring, "Raises", docstring_object.raises)
    init_docstring = add_string(
            init_docstring,
            "Example",
            docstring_object.example.replace("\n", "\n\t") if docstring_object.example else None
    )
    init_docstring = add_string(init_docstring, "Yields", docstring_object.yields)
    return init_docstring

def build_module_docstring_from_object(docstring_object: ModuleDocstring) -> str:
    init_docstring = docstring_object.summary
    if docstring_object.additional_info is not None:
        init_docstring += "\n\n" + docstring_object.additional_info

    if docstring_object.usage is not None:
        init_docstring += "\n\nUsage:\n\t" + docstring_object.usage

    if docstring_object.additional_info or docstring_object.usage:
        init_docstring += "\n"

    return init_docstring

def calculate_indentation(function_code: str) -> str:
    function_code = function_code.strip()
    sol = function_code.find('\n') + 1
    func_without_def = function_code[sol:]
    first_non_whitespace = re.search(r'\S', func_without_def).start(0) # type: ignore
    indentation = func_without_def[:first_non_whitespace]
    return indentation

def add_indentation(docstring: str, indentation: str) -> str:
    docstring = indentation + docstring
    docstring = re.sub(r'\n([^\n])', '\n' + indentation + r'\1', docstring)
    if indentation != "\t":
        docstring = docstring.replace("\t", indentation)
    return docstring

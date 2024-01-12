import re

from typing import Optional

from docgen.pydantic_models import DocString
from docgen.code_parsing import calculate_indentation

def build_docstring(docstring_object: DocString) -> str:
    init_docstring = f'"""{docstring_object.summary}\n\n{docstring_object.description}\n\n'


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
    
    init_docstring = add_list(init_docstring, "Args", docstring_object.parameters)
    init_docstring = add_string(init_docstring, "Returns", docstring_object.returns)
    init_docstring = add_list(init_docstring, "Raises", docstring_object.raises)
    init_docstring = add_string(
            init_docstring,
            "Example",
            docstring_object.example.replace("\n", "\n\t") if docstring_object.example else None
    )
    init_docstring = add_string(init_docstring, "Yields", docstring_object.yields)

    init_docstring += '"""'

    return init_docstring



def add_indentation(docstring: str, function_code: str) -> str:
    indentation = calculate_indentation(function_code)
    docstring = indentation + docstring
    docstring = re.sub(r'\n([^\n])', '\n' + indentation + r'\1', docstring).rstrip()
    docstring = docstring.replace("\t", indentation)
    return docstring

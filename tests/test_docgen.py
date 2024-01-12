import pytest

from docgen.docgen import get_used_functions

@pytest.fixture()
def ex_func():
    from docgen.pydantic_models import DocString
    return {"some_function": DocString(function_name="some_function", summary="This is a docstring", description="This is a description")}

def test_get_used_functions_in_other_module(ex_func):


    function_code = "some_function()"
    imports = ["some_module"]

    visited = {"some_module": ex_func}

    used_functions = get_used_functions(function_code, "", imports, visited, {})

    assert used_functions == [("some_function", "This is a docstring")]

def test_get_used_functions_in_same_module(ex_func):

    function_code = "some_function()"
    imports = []

    visited = {"this_module": ex_func}

    used_functions = get_used_functions(function_code, "this_module", imports, visited, {})

    assert used_functions == [("some_function", "This is a docstring")]


def test_get_used_functions_in_other_module_with_alias(ex_func):
    
    # at the top of their module they have: `from some_module import some_function as aliased_function`

    function_code = "aliased_function()"
    imports = ["some_module"]
    visited = {"some_module": ex_func}
    aliases = {"some_function": "aliased_function"}

    used_functions = get_used_functions(function_code, "", imports, visited, aliases)

    assert used_functions == [("aliased_function", "This is a docstring")]

import ast

from unittest.mock import patch

from docgen.imports import process_import_statement, get_module_imports

def call_process_import_statement(
        tree: ast.Module,
        current_package: str
) -> tuple[list, list, list]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            return process_import_statement(node, current_package)

    return [], [], []


# non relative imports

def test_process_import_statement():
    
    code = "import package.foo"
    tree = ast.parse(code)

    module, function, alias = call_process_import_statement(tree, "package")

    assert module == ["package.foo"]
    assert function == [None]
    assert alias == [None]

def test_process_import_statement_with_alias():
    
    code = "import package.foo as bar"
    tree = ast.parse(code)
    
    module, function, alias = call_process_import_statement(tree, "package")

    assert module == ["package.foo"]
    assert function == [None]
    assert alias == ["bar"]


def test_process_import_with_submodule():

    code = "import package.foo.bar as baz"
    tree = ast.parse(code)

    module, function, alias = call_process_import_statement(tree, "package")

    assert module == ["package.foo.bar"]
    assert function == [None]
    assert alias == ["baz"]

def test_process_import_with_submodule_inside_subpackage():

    code = "import package.foo.bar as baz"
    tree = ast.parse(code)

    module, function, alias = call_process_import_statement(tree, "package.foo")

    assert module == ["package.foo.bar"]
    assert function == [None]
    assert alias == ["baz"]

def test_process_import_from_statement_bar_is_module():

    code = "from package.foo import bar"
    tree = ast.parse(code)
    
    with patch("importlib.import_module") as mock_import_module:
        mock_import_module.return_value = None
        module, function, alias = call_process_import_statement(tree, "package")

    assert module == ["package.foo.bar"]
    assert function == [None]
    assert alias == [None]

def test_process_import_from_statement_bar_is_function():

    code = "from package.foo import bar"
    tree = ast.parse(code)
    
    with patch("importlib.import_module") as mock_import_module:
        mock_import_module.side_effect = ModuleNotFoundError
        module, function, alias = call_process_import_statement(tree, "package")

    assert module == ["package.foo"]
    assert function == ["bar"]
    assert alias == [None]

# relative imports
def test_process_import_from_statement_same_level_import_function():

    code = "from .foo import bar"
    tree = ast.parse(code)
    
    with patch("importlib.import_module") as mock_import_module:
        mock_import_module.side_effect = ModuleNotFoundError
        module, function, alias = call_process_import_statement(tree, "package")

    assert module == ["package.foo"]
    assert function == ["bar"]
    assert alias == [None]

def test_process_import_import_module_with_from_same_level():

    code = "from . import foo"
    tree = ast.parse(code)

    with patch("importlib.import_module") as mock_import_module:
        mock_import_module.return_value = None
        module, function, alias = call_process_import_statement(tree, "package")

    assert module == ["package.foo"]
    assert function == [None]
    assert alias == [None]

def test_process_import_import_module_with_from_same_level_with_alias():

    code = "from . import foo as bar"
    tree = ast.parse(code)

    with patch("importlib.import_module") as mock_import_module:
        mock_import_module.return_value = None
        module, function, alias = call_process_import_statement(tree, "package")

    assert module == ["package.foo"]
    assert function == [None]
    assert alias == ["bar"]

def test_process_import_from_two_dots():

    code = "from .. import foo as bar"
    tree = ast.parse(code)
    
    with patch("importlib.import_module") as mock_import_module:
        mock_import_module.return_value = None
        module, function, alias = call_process_import_statement(tree, "package.baz")

    assert module == ["package.foo"]
    assert function == [None]
    assert alias == ["bar"]

def test_process_import_from_state_upper_level_import():
    # here we are in a module called foo.bar.baz, and we want to import foo.foo.baz
    # we need to go up two levels to get to foo, then import foo.foo.baz

    code = "from ..foo import baz"
    tree = ast.parse(code)
    
    with patch("importlib.import_module") as mock_import_module:
        mock_import_module.side_effect = ModuleNotFoundError
        module, function, alias = call_process_import_statement(tree, "package.bar")

    assert module == ["package.foo"]
    assert function == ["baz"]
    assert alias == [None]

def test_process_import_multiple_imports():

    code = "import package.foo, package.bar, package.baz"
    tree = ast.parse(code)

    module, function, alias = call_process_import_statement(tree, "package")
    
    assert module == ["package.foo", "package.bar", "package.baz"]
    assert function == [None, None, None]
    assert alias == [None, None, None]

def test_process_import_multiple_imports_with_aliases():

    code = "import package.foo as f, package.bar, package.baz as z"
    tree = ast.parse(code)

    module, function, alias = call_process_import_statement(tree, "package")

    assert module == ["package.foo", "package.bar", "package.baz"]
    assert function == [None, None, None]
    assert alias == ["f", None, "z"]

def test_process_import_from_multiple_imports():

    code = "from .foo import bar, baz"
    tree = ast.parse(code)
    
    with patch("importlib.import_module") as mock_import_module:
        mock_import_module.side_effect = ModuleNotFoundError
        module, function, alias = call_process_import_statement(tree, "package")

    assert module == ["package.foo", "package.foo"]
    assert function == ["bar", "baz"]
    assert alias == [None, None]

def test_get_module_imports_modules_imported_empty():

    tree = ast.parse("print(\"hello world\")")
    aliases = get_module_imports(tree, set(), "package")

    assert aliases == {}


def test_get_module_imports_all_functions_imported_directly():
    
    tree = ast.parse("from .foo import bar, baz")
    aliases = get_module_imports(tree, set(["package.foo"]), "package")

    assert aliases == {"bar": "package.foo.bar", "baz": "package.foo.baz"}

def test_get_module_imports_module_aliased():

    tree = ast.parse("import package.foo as foo")
    aliases = get_module_imports(tree, set(["package.foo"]), "package")

    assert aliases == {"foo": "package.foo"}

def test_get_module_imports_function_aliased():

    tree = ast.parse("from package.foo import bar as baz")
    with patch("importlib.import_module") as mock_import_module:
        mock_import_module.side_effect = ModuleNotFoundError
        aliases = get_module_imports(tree, set(["package.foo"]), "package")

    assert aliases == {"baz": "package.foo.bar"}

def test_get_module_imports_from_module_aliased():

    tree = ast.parse("from package.foo import bar as baz")
    with patch("importlib.import_module") as mock_import_module:
        mock_import_module.return_value = None
        aliases = get_module_imports(tree, set(["package.foo.bar"]), "package")

    assert aliases == {"baz": "package.foo.bar"}

def test_get_module_imports_relative():

    tree = ast.parse("from . import foo as bar")
    with patch("importlib.import_module") as mock_import_module:
        mock_import_module.return_value = None
        aliases = get_module_imports(tree, set(["package.foo"]), "package")

    assert aliases == {"bar": "package.foo"}

def test_get_module_imports_not_in_modules_imported():

    tree = ast.parse("from package.foo import bar as baz")
    
    aliases = get_module_imports(tree, set(["package.bar"]), "package")

    assert aliases == {}


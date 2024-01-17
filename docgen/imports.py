"""This module contains functions for handling imports."""
import ast
import importlib


def process_import_from_statement(
        names: list,
        aliases: list,
        level: int,
        module: str | None,
        current_package: str
) -> tuple[list, list, list]:

    """Process an import from statement into a list of modules, functions and aliases.

    Args:
        names (list): list of names imported, either functions or modules.
        aliases (list): list of aliases for the names imported.
        level (int): how relative the import is.
        module (str): the module the import is from. It should be none if the import is '.' or '..', etc.
        current_package (str): the current package being processed.

    Returns:
        tuple[list, list, list]: the modules, functions and aliases.

    Example:
        > process_import_from_statement(["foo"], ["bar"], 1, None, "package") # from . import foo as bar
        returns: (["package.foo"], [None], ["bar"]) if bar is module, else (["package"], ["foo"], ["bar"])

        > process_import_from_statement(["foo"], ["bar"], 2, "package.baz", "package.baz") # from .. import foo as bar
        returns: (["package.foo"], [None], ["bar"]) if bar is module, else (["package"], ["foo"], ["bar"])
    """
    full_module = (
            current_package + ("." + module if module else "")
            if level == 1
            else ".".join(current_package.split(".")[:level - 1]) + ("." + module if module else "")
            if level >= 2
            else module
    )
    try:
        new_names = []
        for name in names:
            importlib.import_module(f"{full_module}.{name}")
            new_names.append(f"{full_module}.{name}")
        return new_names, [None for _ in range(len(names))], aliases
    except ModuleNotFoundError:
        return [full_module for _ in range(len(names))], names, aliases

    


def process_import_statement(
        node: ast.Import | ast.ImportFrom,
        current_package: str
) -> tuple[list, list, list]:
    """Process an import statement into a list of modules, functions and aliases.

    If ImportFrom `process_import_from_statement` is called, else we will just return the names and aliases as you
    cannot import functions from a direct import.

    Args:
        node (ast.Import | ast.ImportFrom): the node to process.
        current_package (str): the current package being processed.

    Returns:
        tuple[list, list, list]: the modules, functions and aliases.
    """

    if not (isinstance(node, ast.ImportFrom) or isinstance(node, ast.Import)):
        raise TypeError("node must be ast.ImportFrom or ast.Import")

    names = [alias.name for alias in node.names]
    aliases = [alias.asname for alias in node.names]

    if isinstance(node, ast.ImportFrom):
        module = node.module
        level = node.level
        return process_import_from_statement(names, aliases, level, module, current_package)

    elif isinstance(node, ast.Import):
        return names, [None for _ in range(len(names))], aliases


def get_module_imports(
        tree: ast.Module,
        modules_imported: set,
        current_package: str
) -> dict:
    """Produce a list of aliases for the imports in the tree.

    Filter out any imports that are not in the modules_imported list. If the import has no alias it will map to itself.

    Args:
        tree (ast.Module): the tree to process.
        modules_imported (list): the modules imported.
        current_package (str): the current package being processed.

    Returns:
        dict: the aliases for the imports.
    """

    output_aliases = {}
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom)):
            continue
        modules, functions, aliases = process_import_statement(node, current_package)
        for module, function, alias in zip(modules, functions, aliases):
            if module not in modules_imported:
                continue

            value_parts = [module]
            if function:
                value_parts.append(function)
            
            value = ".".join(value_parts)
            output_aliases[alias or function] = value
    return output_aliases

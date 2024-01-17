import networkx as nx

from unittest.mock import patch

from docgen.dependencies import (
    build_graph_from_json,
    build_graph_from_nodes_and_edges,
    get_imports,
    is_documentable_file,
)

def test_is_documentable_file_no_init():
    assert is_documentable_file('some_folder/some_file.py') == True

def test_is_documentable_file_init():
    assert is_documentable_file('some_folder/__init__.py') == False

def test_get_imports_no_imports():
    assert get_imports({'file': 'some_file.py'}) == []

def test_get_imports_with_imports():
    assert get_imports({'file': 'some_file.py', 'imports': ['some_import']}) == ['some_import']

def test_build_graph_from_nodes_and_edges():
    nodes = ["node1", "node2"]
    edges = [("node1", "node2")]
    G = build_graph_from_nodes_and_edges(nodes, edges) # type: ignore
    assert list(G.nodes) == ['node1', 'node2']
    assert list(G.edges) == [('node1', 'node2')]
    assert isinstance(G, nx.DiGraph)

@patch('builtins.open')
def test_build_graph_from_json_ignores_init(mock_open):
    with patch('json.load') as mock_load:
        mock_load.return_value = {'some_file.py': {'path': 'some_file.py'}, '__init__.py': {'path': '__init__.py'}}
        G = build_graph_from_json('x')
        assert list(G.nodes) == ['some_file.py']
        assert list(G.edges) == []

@patch('builtins.open')
def test_build_graph_from_json_with_imports(mock_open):
    with patch('json.load') as mock_load:
        mock_load.return_value = {'some_file.py': {'path': 'some_file.py', 'imports': ['some_import']}, 'some_import': {'path': 'some_import'}}
        G = build_graph_from_json('x')
        assert list(G.nodes) == ['some_file.py', 'some_import']
        assert list(G.edges) == [('some_import', 'some_file.py')]

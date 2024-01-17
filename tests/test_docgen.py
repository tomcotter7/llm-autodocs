from docgen.docgen import file_path_to_module_name



def test_file_path_to_module_name_with_path():
    assert file_path_to_module_name("foo/bar.py", "foo") == "foo.bar"

def test_file_path_to_module_name_sub_package():
    assert file_path_to_module_name("foo/bar/baz.py", "foo") == "foo.bar.baz"


def test_file_path_to_module_name_useless_path():
    assert file_path_to_module_name("/home/tcotts/foo/bar.py", "foo") == "foo.bar"

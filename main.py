import argparse

from docgen.docgen import docgen

def main(deps_file):
    docgen(deps_file)
    

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Generate docstrings for your Python code")
    arg_parser.add_argument("--deps_file_path", type=str, required=True)
    args = arg_parser.parse_args()

    main(args.deps_file_path)


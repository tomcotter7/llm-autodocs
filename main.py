import argparse
import logging

from docgen.docgen import docgen

def main(deps_file):
    logging.basicConfig(encoding='utf-8', level=logging.INFO)
    docgen(deps_file)
    

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Generate docstrings for your Python code")
    arg_parser.add_argument("--deps_file_path", type=str, required=True)
    args = arg_parser.parse_args()

    main(args.deps_file_path)


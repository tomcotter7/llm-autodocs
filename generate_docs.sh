pydeps democode --show-deps --no-show --only democode --deps-output deps.json
python3 build_dep_graph.py
python3 docgen.py
sphinx-apidoc -f -o docs/ democode/
make -C docs/ clean
make -C docs/ html

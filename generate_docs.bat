pydeps democode --show-deps --no-show --only democode --deps-output deps.json
py build_dep_graph.py
py docgen.py
sphinx-apidoc -f -o docs/ democode/
make -C docs/ clean
make -C docs/ html


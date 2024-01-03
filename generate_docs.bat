pydeps democode --show-deps --no-show --only democode --deps-output deps.json
py docgen.py
sphinx-apidoc -f -o docs/ democode/
make -C docs/ clean
make -C docs/ html


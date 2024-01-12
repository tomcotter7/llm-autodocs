build-docs:
	sphinx-apidoc -f -o docs/ democode/ && make -C docs/ clean && make -C docs/ html


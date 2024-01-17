PACKAGE_NAME = democode
DEP_OUTPUT = deps.json

build-docs:
	sphinx-apidoc -f -o docs/ $(PACKAGE_NAME)/ && make -C docs/ clean && make -C docs/ html
build-deps:
	pydeps $(PACKAGE_NAME) --show-deps --no-show --only $(PACKAGE_NAME) --deps_output $(DEP_OUTPUT)
run-docgen:
	python3 -m docgen.docgen -d $(DEP_OUTPUT) -p ${PACKAGE_NAME}

entire:
	make build-deps && make run-docgen && make build-docs

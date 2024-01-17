PACKAGE_NAME = democode
DEP_OUTPUT = deps.json

build-deps:
	pydeps $(PACKAGE_NAME) --show-deps --no-show --only $(PACKAGE_NAME) --deps-output $(DEP_OUTPUT)
run-docgen:
	python3 -m docgen.docgen -d $(DEP_OUTPUT) -p ${PACKAGE_NAME}

entire:
	make build-deps && make run-docgen

checkfiles = digicubes/

help:
	@echo  "DigiCubes flask addon development makefile"
	@echo
	@echo  "usage: make <target>"
	@echo  "Targets:"
	@echo  "    up      Updates dev/test dependencies"
	@echo  "    deps    Ensure dev/test dependencies are installed for development"
	@echo  "    lint	Reports all linter violations"

up:
	@pip install -q pip-tools
	CUSTOM_COMPILE_COMMAND="make up" pip-compile -o requirements.txt requirements.in -U
	CUSTOM_COMPILE_COMMAND="make up" pip-compile -o requirements-dev.txt requirements-dev.in -U

deps:
	@pip install -q pip-tools
	@pip install -q wheel
	@pip-sync requirements-dev.txt

lint: deps
	pylint $(checkfiles)

checkdocs:
	doc8 source/

docs:
	sphinx-build -E -b html source build
	sphinx-build -E -b html source_client build_client

ci:	check
	pylint --errors-only $(checkfiles)
	nose2 -v digicubes

nose: deps
	nose2 -v digicubes

check: deps
	black -l 100 --check digicubes/

style:
	black -l 100 digicubes/ 

badges: deps
	python lintbadge.py

pack: ci
	rm -fR dist/
	#python setup_client.py sdist bdist_wheel
	python setup.py sdist bdist_wheel

publish: pack
	twine check ./dist/*
	twine upload ./dist/*

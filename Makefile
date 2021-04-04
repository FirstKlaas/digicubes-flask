checkfiles = digicubes_flask/

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
	doc8 docs/source/

docs: checkdocs
	sphinx-build -E -b html docs/source docs/build

ci:	style check nose
	#pylint --errors-only $(checkfiles)

nose: deps
	nose2 -v digicubes_flask

check: deps
	black -l 100 --check $(checkfiles)

style:
	black -l 100 $(checkfiles)
	isort $(checkfiles)

badges: deps
	python lintbadge.py

pack: ci release babel_compile
	rm -fR dist/
	#python setup_client.py sdist bdist_wheel
	python version.py
	python setup.py sdist bdist_wheel

babel_extract:
	pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .

babel_init:
	pybabel init -i messages.pot -d digicubes_flask/translations -l en
	pybabel init -i messages.pot -d digicubes_flask/translations -l de

babel_update:
	#pybabel init -i messages.pot -d digicubes_flask/translations -l en
	pybabel update -i messages.pot -d digicubes_flask/translations -l en
	pybabel update -i messages.pot -d digicubes_flask/translations -l de

babel_compile:
	pybabel compile -d digicubes_flask/translations

publish: pack
	twine check ./dist/*	
	twine upload ./dist/*

run:
	flask run

docker_gen:
	@python generate_docker_file.py

release: docker_gen
	@python version.py

docker: pack
	docker build -t digicubes-web .

gunicorn:
	gunicorn -b 0.0.0.0:5050 --worker-tmp-dir=/dev/shm --workers=2 --threads=4 --worker-class=gthread wsgi:app

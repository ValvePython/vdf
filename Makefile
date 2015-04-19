# Makefile for VDF module

define HELPBODY
Available commands:

	make help       - this thing.
	make init       - install python dependancies
	make test       - run tests and coverage
	make pylint     - code analysis
	make build      - pylint + test

endef

export HELPBODY
help:
	@echo "$$HELPBODY"

init:
	pip install -r requirements.txt

test:
	rm -f vdf/*.pyc
	nosetests --verbosity 2 --with-coverage --cover-package=vdf

pylint:
	pylint -r n -f colorized vdf || true

build: pylint test

clean:
	rm -rf dist vdf.egg-info vdf/*.pyc

dist: clean
	python setup.py sdist

upload: dist
	python setup.py register -r pypi
	twine upload -r pypi dist/*

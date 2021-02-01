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
	pip install -r dev_requirements.txt

COVOPTS = --cov-config .coveragerc --cov=vdf

ifeq ($(NOCOV), 1)
	COVOPTS =
endif

test:
	rm -f .coverage vdf/*.pyc tests/*.pyc
	PYTHONHASHSEED=0 pytest --tb=short $(COVOPTS) tests

pylint:
	pylint -r n -f colorized vdf || true

build: pylint test

clean:
	rm -rf dist vdf.egg-info vdf/*.pyc

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel --universal

register:
	python setup.py register -r pypi

upload: dist register
	twine upload -r pypi dist/*

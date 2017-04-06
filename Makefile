SHELL := /bin/bash

.PHONY: all
all:
	@python setup.py build

.PHONY: lint
lint:
	@pylint -r n  akcli

.PHONY: test
test:
	@python -m unittest discover

.PHONY: deploy
deploy:
	@python setup.py sdist upload -r pypi

.PHONY: clean
clean:
	@rm -rf build akcli.egg-info

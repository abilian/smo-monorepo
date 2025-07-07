test:
	pytest

.PHONY: test

format:
	cd smo-core && isort .
	cd smo-cli && isort .
	ruff format

.PHONY: format


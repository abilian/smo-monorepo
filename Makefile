test:
	pytest smo-core
	pytest smo-cli

.PHONY: test

format:
	cd smo-core && isort .
	cd smo-cli && isort .
	ruff format

.PHONY: format


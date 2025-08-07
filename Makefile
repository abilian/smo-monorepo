all: lint test

## Help message
help:
	adt help-make


.PHONY: test
## Run tests
test:
	uv run pytest smo-core
	uv run pytest smo-cli
	uv run pytest smo-web


.PHONY: lint
## Run linters on the codebase
lint:
	uv run ruff check


.PHONY: clean
## Clean build artifacts and runtime files
clean:
	adt clean
	cd smo-core && adt clean
	cd smo-cli && adt clean
	cd smo-web && adt clean
	rm -rf examples/brussels-demo/*.tar.gz
	rm -rf dist .nox */.nox 


.PHONY: format
## Format code using isort and ruff
format:
	cd smo-core && isort .
	cd smo-cli && isort .
	cd smo-web && isort .
	cd smo-ui && isort .
	cd smo-sdk && isort .
	ruff format


## Sync code with remote repositories
sync-code:
	git pull origin main
	@make push-code

## Push code to remote repositories
push-code:
	git push origin
	git push eclipse
	git push ci

.PHONY: sync-code push-code

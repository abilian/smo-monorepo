all: lint test

## Help message
help:
	adt help-make


.PHONY: test
## Run tests
test:
	pytest smo-core
	pytest smo-cli


.PHONY: lint
## Run linters on the codebase
lint:
	ruff check


.PHONY: clean
## Clean build artifacts and runtime files
clean:
	cd smo-core && adt clean
	cd smo-cli && adt clean
	rm -rf examples/brussels-demo/*.tar.gz


.PHONY: format
## Format code using isort and ruff
format:
	cd smo-core && isort .
	cd smo-cli && isort .
	ruff format


## Sync code with remote repositories
sync-code:
	git pull origin main
	# git pull gh
	git pull sourcehut main
	@make push-code

## Push code to remote repositories
push-code:
	git push origin main
	# git push gh
	git push sourcehut main

.PHONY: sync-code push-code

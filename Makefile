all: lint test

test:
	pytest smo-core
	pytest smo-cli

.PHONY: test


lint:
	ruff check

.PHONY: test


format:
	cd smo-core && isort .
	cd smo-cli && isort .
	ruff format

.PHONY: format


## Sync code with remote repositories
sync-code:
	git pull origin main
	# git pull gh
	git pull sourcehut main
	@make push-code

.PHONY: sync-code


## Push code to remote repositories
push-code:
	git push origin main
	# git push gh
	git push sourcehut main

.PHONY: push-code

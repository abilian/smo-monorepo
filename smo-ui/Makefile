.PHONY: all test build format check lint clean

all: check test

check: lint

lint:
	ruff check .

test:
	pytest

format:
	isort .
	ruff format .

clean:
	rm -rf .pytest_cache .nox .ruff_cache dist build __pycache__ \
		.mypy_cache .coverage htmlcov .coverage.* *.egg-info

build: clean
	uv build

publish: build
	uv publish


# Specific

.PHONY: run

run:
	granian --interface asgi --factory smo_ui.app:create_app --reload

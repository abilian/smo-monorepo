.PHONY: all test build format check lint clean

all: check test

check: lint

lint:
	ruff check .

test:
	pytest
	nox -s tests

format:
	isort .
	ruff format .

clean:
	rm -rf .pytest_cache .nox .ruff_cache dist build __pycache__ .mypy_cache .coverage htmlcov .coverage.* *.egg-info

build: clean
	uv build

publish: build
	uv publish


# Specific

.PHONY: run

run-fastapi-granian:
	granian --interface asgi --factory smo_web.app:create_app --reload


.PHONY: run
## Run the Smo Web application (in development mode)
run:
	uvicorn smo_web.asgi:app --host 0.0.0.0 --port 8000 --reload
	# granian --interface asgi --factory smo_web.app:create_app --reload

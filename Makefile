VENV := .venv/bin

.PHONY: setup start lint format deadcode check

# One-time setup: install dev tools and git hooks
setup:
	$(VENV)/pip install -r requirements-dev.txt
	$(VENV)/pre-commit install

start:
	$(VENV)/uvicorn main:app --reload

lint:
	$(VENV)/ruff check .

format:
	$(VENV)/ruff check --fix .
	$(VENV)/ruff format .

deadcode:
	$(VENV)/vulture

# Same checks the pre-commit hook runs, on all files
check:
	$(VENV)/ruff check .
	$(VENV)/ruff format --check .
	$(VENV)/vulture

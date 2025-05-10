.PHONY: setup test lint format coverage clean build docs update-deps install-deps

PYTHON = python3.11
VENV = .venv
BIN = $(VENV)/bin
SRC = src/panoptikon
TESTS = tests

setup: $(VENV)/bin/pip
	$(BIN)/pip install -e ".[dev]"
	$(BIN)/pre-commit install

$(VENV)/bin/pip:
	$(PYTHON) -m venv $(VENV)

test:
	$(BIN)/pytest $(TESTS)

lint:
	$(BIN)/ruff check $(SRC) $(TESTS)
	$(BIN)/mypy $(SRC)

format:
	$(BIN)/ruff format $(SRC) $(TESTS)
	$(BIN)/black $(SRC) $(TESTS)
	$(BIN)/isort $(SRC) $(TESTS)

coverage:
	$(BIN)/pytest --cov=$(SRC) --cov-report=html --cov-report=xml --cov-report=term-missing $(TESTS)

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	$(BIN)/pip install build
	$(PYTHON) -m build

docs:
	$(BIN)/sphinx-build -b html docs/source docs/build/html

update-deps:
	$(BIN)/pip install pip-tools
	$(BIN)/pip-compile pyproject.toml -o requirements.txt

install-deps:
	$(BIN)/pip install -r requirements.txt 
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
MYPY = $(VENV)/bin/mypy
FLAKE8 = $(VENV)/bin/flake8
STAMP = $(VENV)/.installed

$(VENV)/bin/activate:
	python3 -m venv $(VENV)

$(STAMP): $(VENV)/bin/activate pyproject.toml
	$(PIP) install --upgrade pip build wheel flake8 mypy pydantic types-setuptools
	$(PIP) install mlx-2.2-py3-none-any.whl
	$(PIP) install -e .
	touch $(STAMP)

install: $(STAMP)

run: install
	$(PYTHON) a_maze_ing.py config.txt


build: install
	$(PYTHON) -m build --sdist --wheel --outdir .
	@echo "\n[i] Package built! Files are in the root directory"

debug: install
	$(PYTHON) -m pdb a_maze_ing.py config.txt

lint: install
	$(FLAKE8) . --exclude=$(VENV),mazegen/__init__.py
	$(MYPY) . --exclude $(VENV) --exclude build

lint-strict: install
	$(FLAKE8) . --exclude=$(VENV),mazegen/__init__.py
	$(MYPY) . --exclude $(VENV) --exclude build --strict

clean:
	rm -rf __pycache__ mazegen/__pycache__
	rm -rf *.egg-info build dist .mypy_cache
	rm -rf maze_output.txt

fclean: clean
	rm -rf $(VENV)

all: install

re: fclean all
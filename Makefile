PYTHONPATH=.
DJANGO_SETTINGS_MODULE=llm_translator.llm_translator.settings
POETRY=poetry

.PHONY: test migrate run shell format lint install clean

# Run tests using pytest within the Poetry-managed virtual environment
test:
	$(POETRY) run env PYTHONPATH=$(PYTHONPATH) DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS_MODULE) pytest

# Apply database migrations using Django's manage.py tool
migrate:
	$(POETRY) run env PYTHONPATH=$(PYTHONPATH) DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS_MODULE) python llm_translator/manage.py migrate

# Start the Django development server on all interfaces at port 8000
run:
	$(POETRY) run env PYTHONPATH=$(PYTHONPATH) DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS_MODULE) python llm_translator/manage.py runserver 0.0.0.0:8000

# Launch the Django shell (useful for debugging and running scripts interactively)
shell:
	$(POETRY) run env PYTHONPATH=$(PYTHONPATH) DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS_MODULE) python llm_translator/manage.py shell

# Format Python code in the `llm_translator/` directory using Black
format:
	$(POETRY) run black llm_translator/

# Lint the code in `llm_translator/` using Flake8 to check for style issues
lint:
	$(POETRY) run flake8 llm_translator/

# Install all dependencies defined in pyproject.toml using Poetry
install:
	$(POETRY) install
# Clean up compiled Python files and __pycache__ directories
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} + 

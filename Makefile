PYTHONPATH=.
DJANGO_SETTINGS_MODULE=llm_translator.llm_translator.settings
POETRY=poetry

.PHONY: test migrate run shell format lint install clean

test:
	$(POETRY) run env PYTHONPATH=$(PYTHONPATH) DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS_MODULE) pytest

migrate:
	$(POETRY) run env PYTHONPATH=$(PYTHONPATH) DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS_MODULE) python llm_translator/manage.py migrate

run:
	$(POETRY) run env PYTHONPATH=$(PYTHONPATH) DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS_MODULE) python llm_translator/manage.py runserver 0.0.0.0:8000

shell:
	$(POETRY) run env PYTHONPATH=$(PYTHONPATH) DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS_MODULE) python llm_translator/manage.py shell

format:
	$(POETRY) run black llm_translator/

lint:
	$(POETRY) run flake8 llm_translator/

install:
	$(POETRY) install

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} + 
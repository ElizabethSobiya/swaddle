SHELL := /bin/bash
VENV := .venv
PYTHON := $(VENV)/bin/python

.PHONY: install dev test seed

install:
	npm install
	python3.11 -m venv $(VENV)
	$(VENV)/bin/pip install -e "server[dev]"

dev:
	@test -x "$(PYTHON)" || (echo "Run 'make install' first." && exit 1)
	docker compose up -d db
	@trap 'kill 0' INT TERM EXIT; \
		$(PYTHON) -m uvicorn app.main:app --app-dir server --reload --port 8001 & \
		npm --workspace @swaddle/client run dev & \
		wait

test:
	npm --workspace @swaddle/client run test
	$(PYTHON) -m pytest server
	$(PYTHON) -m ruff check server shared/types
	$(PYTHON) -m black --check server shared/types

seed:
	@test -x "$(PYTHON)" || (echo "Run 'make install' first." && exit 1)
	$(PYTHON) -m alembic -c server/alembic.ini upgrade head
	PYTHONPATH=server $(PYTHON) server/scripts/seed.py

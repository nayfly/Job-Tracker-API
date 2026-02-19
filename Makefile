# Makefile shortcuts for common tasks

.PHONY: test lint up

test:
	python -m pytest -q

lint:
	ruff check --fix .

up:
	docker-compose up

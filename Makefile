MAKEFILE_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
DEV_ENV_FILE := deployment/.env.dev
PROD_ENV_FILE := deployment/.env.prod

.PHONY: help dev-build dev-up dev-down dev-logs dev-clean dev-shell restart-dev-app prod-build prod-up prod-down prod-logs prod-clean prod-shell db-migrate db-upgrade test lint format up down logs shell

help:
	@echo "Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  dev-build      Build development containers"
	@echo "  dev-up         Start development environment"
	@echo "  dev-down       Stop development environment"
	@echo "  dev-logs       Show development logs"
	@echo "  dev-clean      Clean development resources"
	@echo "  dev-shell      Open shell in development app container"
	@echo "  restart-dev-app Restart development application"
	@echo ""
	@echo "Production:"
	@echo "  prod-build     Build production containers"
	@echo "  prod-up        Start production environment"
	@echo "  prod-down      Stop production environment"
	@echo "  prod-logs      Show production logs"
	@echo "  prod-clean     Clean production resources"
	@echo "  prod-shell     Open shell in production app container"
	@echo ""
	@echo "Database:"
	@echo "  db-migrate     Run database migrations"
	@echo "  db-upgrade     Upgrade database to latest revision"
	@echo ""
	@echo "Quality:"
	@echo "  test           Run tests"
	@echo "  lint           Run linting"
	@echo "  format         Format code"
	@echo ""
	@echo "Legacy (dev):"
	@echo "  up             Alias for dev-up"
	@echo "  down           Alias for dev-down"
	@echo "  logs           Alias for dev-logs"
	@echo "  shell          Alias for dev-shell"

dev-build:
	cd "$(MAKEFILE_DIR)" && docker compose --env-file $(DEV_ENV_FILE) -f deployment/docker-compose.dev.yml build

dev-up:
	cd "$(MAKEFILE_DIR)" && docker compose --env-file $(DEV_ENV_FILE) -f deployment/docker-compose.dev.yml up -d

restart-dev-app:
	cd "$(MAKEFILE_DIR)" && docker compose --env-file $(DEV_ENV_FILE) -f deployment/docker-compose.dev.yml restart app

dev-down:
	cd "$(MAKEFILE_DIR)" && docker compose --env-file $(DEV_ENV_FILE) -f deployment/docker-compose.dev.yml down

dev-logs:
	cd "$(MAKEFILE_DIR)" && docker compose --env-file $(DEV_ENV_FILE) -f deployment/docker-compose.dev.yml logs -f

dev-clean:
	cd "$(MAKEFILE_DIR)" && docker compose --env-file $(DEV_ENV_FILE) -f deployment/docker-compose.dev.yml down -v --remove-orphans
	docker system prune -f

dev-shell:
	cd "$(MAKEFILE_DIR)" && docker compose --env-file $(DEV_ENV_FILE) -f deployment/docker-compose.dev.yml exec -it app sh

prod-build:
	cd "$(MAKEFILE_DIR)" && docker compose --env-file $(PROD_ENV_FILE) -f deployment/docker-compose.prod.yml build

prod-up:
	cd "$(MAKEFILE_DIR)" && docker compose --env-file $(PROD_ENV_FILE) -f deployment/docker-compose.prod.yml up -d --build

prod-down:
	cd "$(MAKEFILE_DIR)" && docker compose --env-file $(PROD_ENV_FILE) -f deployment/docker-compose.prod.yml down

prod-logs:
	cd "$(MAKEFILE_DIR)" && docker compose --env-file $(PROD_ENV_FILE) -f deployment/docker-compose.prod.yml logs -f

prod-clean:
	cd "$(MAKEFILE_DIR)" && docker compose --env-file $(PROD_ENV_FILE) -f deployment/docker-compose.prod.yml down -v --remove-orphans
	docker system prune -f

prod-shell:
	cd "$(MAKEFILE_DIR)" && docker compose --env-file $(PROD_ENV_FILE) -f deployment/docker-compose.prod.yml exec -it app sh

db-migrate:
	cd "$(MAKEFILE_DIR)" && docker compose --env-file $(DEV_ENV_FILE) -f deployment/docker-compose.dev.yml exec -T app alembic upgrade head

db-upgrade:
	cd "$(MAKEFILE_DIR)" && docker compose --env-file $(DEV_ENV_FILE) -f deployment/docker-compose.dev.yml exec -T app alembic upgrade head

test:
	cd "$(MAKEFILE_DIR)" && docker compose --env-file $(DEV_ENV_FILE) -f deployment/docker-compose.dev.yml exec app python -m pytest

lint:
	cd "$(MAKEFILE_DIR)" && uv run ruff check src/
	cd "$(MAKEFILE_DIR)" && uv run mypy src/

format:
	cd "$(MAKEFILE_DIR)" && uv run ruff format src/

up: dev-up
down: dev-down
logs: dev-logs
shell: dev-shell

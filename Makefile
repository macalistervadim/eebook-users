export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

all: down build up test exec-api

build:
	docker compose build

up:
	docker compose up
	
down:
	docker compose down

test:
	docker compose exec app pytest

exec-api:
	docker compose exec app sh

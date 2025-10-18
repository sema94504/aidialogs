.PHONY: help lint format typecheck test coverage run run-api run-api-mock test-api clean install-services start stop status logs logs-watcher
.PHONY: frontend-dev frontend-lint frontend-typecheck frontend-build
.PHONY: docker-up docker-down docker-logs docker-logs-bot docker-logs-api docker-logs-frontend docker-status docker-build docker-clean
.PHONY: registry-pull registry-up registry-down registry-logs

.DEFAULT_GOAL := help

help:
	@echo "════════════════════════════════════════════════════════════════"
	@echo "  AIDialogs - Available Commands"
	@echo "════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Backend (Python):"
	@echo "  make run              Run Telegram bot"
	@echo "  make run-api          Run API server (Real DB)"
	@echo "  make run-api-mock     Run API server (Mock data)"
	@echo "  make test             Run tests"
	@echo "  make coverage         Run tests with coverage"
	@echo "  make lint             Run linter (ruff)"
	@echo "  make format           Format code (ruff)"
	@echo "  make typecheck        Run type checker (mypy)"
	@echo "  make test-api         Test API endpoint with curl"
	@echo ""
	@echo "Frontend (Next.js):"
	@echo "  make frontend-dev     Run frontend dev server"
	@echo "  make frontend-lint    Run frontend linter"
	@echo "  make frontend-typecheck  Run frontend type checker"
	@echo "  make frontend-build   Build frontend for production"
	@echo ""
	@echo "Services (systemd):"
	@echo "  make install-services Install systemd services"
	@echo "  make start            Start services"
	@echo "  make stop             Stop services"
	@echo "  make status           Show services status"
	@echo "  make logs             Show bot logs"
	@echo "  make logs-watcher     Show watcher logs"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up        Start all services with Docker Compose"
	@echo "  make docker-down      Stop all services"
	@echo "  make docker-logs      Show logs from all services"
	@echo "  make docker-logs-bot  Show bot logs"
	@echo "  make docker-logs-api  Show API logs"
	@echo "  make docker-logs-frontend  Show frontend logs"
	@echo "  make docker-status    Show services status"
	@echo "  make docker-build     Build Docker images"
	@echo "  make docker-clean     Stop and remove all containers and volumes"
	@echo ""
	@echo "Registry (GitHub Container Registry):"
	@echo "  make registry-pull    Pull images from ghcr.io"
	@echo "  make registry-up      Start services with registry images"
	@echo "  make registry-down    Stop registry services"
	@echo "  make registry-logs    Show registry services logs"
	@echo ""
	@echo "Misc:"
	@echo "  make clean            Clean cache and logs"
	@echo ""
	@echo "════════════════════════════════════════════════════════════════"

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

typecheck:
	uv run mypy src/

test:
	uv run pytest tests/ -v

coverage:
	uv run pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

run:
	uv run python -m src.main

run-api:
	uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-api-mock:
	USE_MOCK_STATS=true uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

test-api:
	@echo "Testing API endpoint..."
	@curl -s http://localhost:8000/api/stats | python -m json.tool || echo "API not running. Start with: make run-api"

clean:
	rm -rf .pytest_cache __pycache__ src/__pycache__ tests/__pycache__
	rm -rf htmlcov .coverage
	rm -f bot.log

install-services:
	sudo cp aidialogs-bot.service /etc/systemd/system/
	sudo cp aidialogs-watcher.service /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable aidialogs-bot
	sudo systemctl enable aidialogs-watcher
	@echo "Services installed and enabled"

start:
	sudo systemctl start aidialogs-bot
	sudo systemctl start aidialogs-watcher
	@echo "Services started"

stop:
	sudo systemctl stop aidialogs-bot
	sudo systemctl stop aidialogs-watcher
	@echo "Services stopped"

status:
	@echo "=== Bot Service Status ==="
	sudo systemctl status aidialogs-bot --no-pager
	@echo ""
	@echo "=== Watcher Service Status ==="
	sudo systemctl status aidialogs-watcher --no-pager

logs:
	sudo journalctl -u aidialogs-bot -f

logs-watcher:
	sudo journalctl -u aidialogs-watcher -f

frontend-dev:
	cd frontend && pnpm dev

frontend-lint:
	cd frontend && pnpm lint

frontend-typecheck:
	cd frontend && pnpm typecheck

frontend-build:
	cd frontend && pnpm build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-logs-bot:
	docker compose logs -f bot

docker-logs-api:
	docker compose logs -f api

docker-logs-frontend:
	docker compose logs -f frontend

docker-status:
	docker compose ps

docker-build:
	docker compose build

docker-clean:
	docker compose down -v

registry-pull:
	@echo "Pulling images from GitHub Container Registry..."
	./scripts/registry-pull.sh $(GITHUB_USER) latest pull

registry-up:
	@echo "Starting services with registry images..."
	./scripts/registry-pull.sh $(GITHUB_USER) latest up

registry-down:
	@echo "Stopping registry services..."
	./scripts/registry-pull.sh $(GITHUB_USER) latest down

registry-logs:
	docker compose -f docker-compose.registry.yml logs -f

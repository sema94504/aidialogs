.PHONY: lint format typecheck test coverage run run-api test-api clean install-services start stop status logs logs-watcher

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

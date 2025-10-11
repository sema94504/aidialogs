.PHONY: lint format test coverage run clean

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

test:
	uv run pytest tests/ -v

coverage:
	uv run pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

run:
	cd src && uv run python main.py

clean:
	rm -rf .pytest_cache __pycache__ src/__pycache__ tests/__pycache__
	rm -rf htmlcov .coverage
	rm -f bot.log


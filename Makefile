.PHONY: test run clean

test:
	uv run pytest tests/ -v

run:
	cd src && uv run python main.py

clean:
	rm -rf .pytest_cache __pycache__ src/__pycache__ tests/__pycache__
	rm -f bot.log


.PHONY: test run clean install-services start stop status logs logs-watcher

test:
	uv run pytest tests/ -v

run:
	cd src && uv run python main.py

clean:
	rm -rf .pytest_cache __pycache__ src/__pycache__ tests/__pycache__
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


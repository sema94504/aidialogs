#!/usr/bin/env bash
set -e

sudo systemctl stop aidialogs-bot aidialogs-watcher 2>/dev/null || true
sudo cp aidialogs-bot.service /etc/systemd/system/
sudo cp aidialogs-watcher.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start aidialogs-bot
sudo systemctl start aidialogs-watcher
echo "Services reinstalled and started"


#!/usr/bin/env bash

set -e

REPO_DIR="/opt/aidialogs"
LOG_FILE="/opt/aidialogs/git-watcher.log"
CHECK_INTERVAL=60

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Git watcher started"

cd "$REPO_DIR"

while true; do
    log "Checking for updates..."
    
    git fetch origin main 2>&1 | tee -a "$LOG_FILE"
    
    LOCAL_HASH=$(git rev-parse HEAD)
    REMOTE_HASH=$(git rev-parse origin/main)
    
    if [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
        log "Changes detected: $LOCAL_HASH -> $REMOTE_HASH"
        log "Pulling updates..."
        
        git pull origin main 2>&1 | tee -a "$LOG_FILE"
        
        log "Restarting bot service..."
        systemctl restart aidialogs-bot 2>&1 | tee -a "$LOG_FILE"
        
        log "Bot service restarted successfully"
    else
        log "No updates found"
    fi
    
    sleep "$CHECK_INTERVAL"
done


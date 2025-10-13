#!/usr/bin/env bash

REPO_DIR="/opt/aidialogs"
LOG_FILE="/opt/aidialogs/git-watcher.log"
CHECK_INTERVAL=60

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

touch "$LOG_FILE" 2>/dev/null || true
chmod 666 "$LOG_FILE" 2>/dev/null || true

log "Git watcher started"

cd "$REPO_DIR"

if ! git config --global --get-all safe.directory 2>/dev/null | grep -q "^/opt/aidialogs$"; then
    git config --global --add safe.directory /opt/aidialogs 2>/dev/null || true
    log "Added /opt/aidialogs to git safe.directory"
fi

git config pull.rebase false 2>/dev/null || true

while true; do
    log "Checking for updates..."
    
    git fetch origin main 2>&1 | tee -a "$LOG_FILE" || true
    
    LOCAL_HASH=$(git rev-parse HEAD 2>/dev/null)
    REMOTE_HASH=$(git rev-parse origin/main 2>/dev/null)
    
    if [ "$LOCAL_HASH" != "$REMOTE_HASH" ] && [ -n "$LOCAL_HASH" ] && [ -n "$REMOTE_HASH" ]; then
        log "Changes detected: $LOCAL_HASH -> $REMOTE_HASH"
        log "Pulling updates..."
        
        git pull origin main 2>&1 | tee -a "$LOG_FILE" || true
        
        log "Restarting bot service..."
        sudo systemctl restart aidialogs-bot 2>&1 | tee -a "$LOG_FILE"
        
        log "Bot service restarted successfully"
    else
        log "No updates found"
    fi
    
    sleep "$CHECK_INTERVAL"
done


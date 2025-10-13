#!/usr/bin/env bash

set -e

SUDOERS_FILE="/etc/sudoers.d/aidialogs-watcher"

echo "Creating sudoers rule for aidialogs-watcher..."

sudo bash -c "cat > $SUDOERS_FILE" << 'EOF'
# Allow semion to restart aidialogs-bot without password
semion ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart aidialogs-bot
EOF

sudo chmod 0440 "$SUDOERS_FILE"

echo "Sudoers rule created: $SUDOERS_FILE"
echo "User 'semion' can now restart aidialogs-bot without password"


#!/bin/bash
# Archon Launcher Script
# Starts Archon containers and opens browser when ready

ARCHON_DIR="/home/hammer/Documents/repos/Archon"
FRONTEND_URL="http://localhost:3737"
MAX_WAIT=60

cd "$ARCHON_DIR"

# Check if already running
if curl -s "$FRONTEND_URL" > /dev/null 2>&1; then
    echo "Archon is already running!"
else
    # Start containers (only rebuild if not running)
    docker compose up --build -d

    # Wait for frontend to be ready
    echo "Waiting for Archon to start..."
    for i in $(seq 1 $MAX_WAIT); do
        if curl -s "$FRONTEND_URL" > /dev/null 2>&1; then
            echo "Archon is ready!"
            break
        fi
        sleep 1
    done
fi

# Open browser - try multiple methods
if command -v firefox &> /dev/null; then
    firefox "$FRONTEND_URL" &
elif command -v google-chrome &> /dev/null; then
    google-chrome "$FRONTEND_URL" &
elif command -v chromium-browser &> /dev/null; then
    chromium-browser "$FRONTEND_URL" &
else
    # Fallback to xdg-open with DISPLAY set
    DISPLAY="${DISPLAY:-:0}" xdg-open "$FRONTEND_URL" &
fi

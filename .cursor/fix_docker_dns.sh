#!/bin/bash
# Fix Docker DNS configuration to prevent intermittent DNS resolution failures

LOG_FILE="/home/hammer/Documents/repos/Archon/.cursor/debug.log"

log() {
    local message="$1"
    local data="$2"
    local hypothesis_id="$3"
    local timestamp=$(date +%s%3N)
    local log_entry=$(cat <<EOF
{"id":"log_${timestamp}_$$","timestamp":${timestamp},"location":"fix_docker_dns.sh","message":"${message}","data":${data},"sessionId":"debug-session","runId":"fix","hypothesisId":"${hypothesis_id}"}
EOF
)
    echo "$log_entry" >> "$LOG_FILE"
    echo "[FIX] $message"
}

DAEMON_JSON="/etc/docker/daemon.json"
BACKUP_JSON="/etc/docker/daemon.json.backup.$(date +%Y%m%d_%H%M%S)"

log "Starting Docker DNS fix" "{\"daemon_json_path\":\"$DAEMON_JSON\"}" "FIX"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    log "Not running as root - checking if sudo is available" "{\"user\":\"$(whoami)\"}" "FIX"
    SUDO_CMD="sudo"
    if ! command -v sudo &> /dev/null; then
        echo "ERROR: This script must be run as root or with sudo"
        log "ERROR: Cannot proceed without root/sudo" "{\"error\":\"no_sudo\"}" "FIX"
        exit 1
    fi
else
    SUDO_CMD=""
    log "Running as root" "{}" "FIX"
fi

# Check if daemon.json exists
if [ -f "$DAEMON_JSON" ]; then
    log "Backing up existing daemon.json" "{\"backup\":\"$BACKUP_JSON\"}" "FIX"
    $SUDO_CMD cp "$DAEMON_JSON" "$BACKUP_JSON"
    EXISTING_CONTENT=$($SUDO_CMD cat "$DAEMON_JSON")
    log "Existing daemon.json content" "{\"content\":\"$EXISTING_CONTENT\"}" "FIX"
else
    log "daemon.json does not exist - will create new" "{}" "FIX"
    EXISTING_CONTENT="{}"
fi

# Create directory if it doesn't exist
$SUDO_CMD mkdir -p /etc/docker
log "Created /etc/docker directory if needed" "{}" "FIX"

# Parse existing JSON and merge DNS config
# Use Python for reliable JSON manipulation
NEW_JSON=$(python3 <<EOF
import json
import sys

try:
    if "$EXISTING_CONTENT":
        config = json.loads('$EXISTING_CONTENT')
    else:
        config = {}
except:
    config = {}

# Configure DNS servers
# Primary: Google DNS, Secondary: Cloudflare DNS, Fallback: systemd-resolved
dns_servers = ["8.8.8.8", "1.1.1.1", "127.0.0.53"]

# Merge DNS config (preserve existing if present, but add our reliable ones)
if "dns" in config:
    existing_dns = config["dns"]
    # Merge, prioritizing our reliable DNS servers
    merged_dns = dns_servers + [d for d in existing_dns if d not in dns_servers]
    config["dns"] = merged_dns
    print("Merged with existing DNS config", file=sys.stderr)
else:
    config["dns"] = dns_servers
    print("Added new DNS config", file=sys.stderr)

print(json.dumps(config, indent=2))
EOF
)

log "Generated new daemon.json configuration" "{\"config\":\"$NEW_JSON\"}" "FIX"

# Write new configuration
echo "$NEW_JSON" | $SUDO_CMD tee "$DAEMON_JSON" > /dev/null
if [ $? -eq 0 ]; then
    log "Successfully wrote daemon.json" "{}" "FIX"
else
    log "ERROR: Failed to write daemon.json" "{\"exit_code\":$?}" "FIX"
    exit 1
fi

# Validate JSON
if ! echo "$NEW_JSON" | python3 -m json.tool > /dev/null 2>&1; then
    log "ERROR: Generated JSON is invalid" "{}" "FIX"
    if [ -f "$BACKUP_JSON" ]; then
        log "Restoring backup" "{\"backup\":\"$BACKUP_JSON\"}" "FIX"
        $SUDO_CMD cp "$BACKUP_JSON" "$DAEMON_JSON"
    fi
    exit 1
fi

log "JSON validation passed" "{}" "FIX"

# Restart Docker daemon
log "Restarting Docker daemon to apply changes" "{}" "FIX"
if $SUDO_CMD systemctl restart docker; then
    log "Docker daemon restarted successfully" "{}" "FIX"
else
    log "WARNING: Docker daemon restart may have failed" "{\"exit_code\":$?}" "FIX"
    echo "WARNING: Please manually restart Docker: sudo systemctl restart docker"
fi

# Wait a moment for Docker to be ready
sleep 2

# Verify Docker is running
if docker info > /dev/null 2>&1; then
    log "Docker daemon is running after restart" "{}" "FIX"
    echo ""
    echo "✅ Docker DNS configuration updated successfully!"
    echo "   DNS servers configured: 8.8.8.8, 1.1.1.1, 127.0.0.53"
    if [ -f "$BACKUP_JSON" ]; then
        echo "   Backup saved to: $BACKUP_JSON"
    fi
    echo ""
    echo "Test the fix by running: docker compose up --build -d"
else
    log "ERROR: Docker daemon is not responding after restart" "{}" "FIX"
    echo "ERROR: Docker daemon is not responding. Please check: sudo systemctl status docker"
    exit 1
fi

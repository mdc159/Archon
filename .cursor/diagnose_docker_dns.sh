#!/bin/bash
# Diagnostic script for Docker DNS issues

LOG_FILE="/home/hammer/Documents/repos/Archon/.cursor/debug.log"

log() {
    local message="$1"
    local data="$2"
    local hypothesis_id="$3"
    local timestamp=$(date +%s%3N)
    local log_entry=$(cat <<EOF
{"id":"log_${timestamp}_$$","timestamp":${timestamp},"location":"diagnose_docker_dns.sh","message":"${message}","data":${data},"sessionId":"debug-session","runId":"diagnostic","hypothesisId":"${hypothesis_id}"}
EOF
)
    echo "$log_entry" >> "$LOG_FILE"
    echo "[DEBUG] $message"
}

echo "=== Docker DNS Diagnostic Script ==="
echo "Testing DNS resolution and Docker connectivity..."
echo ""

# Test 1: DNS resolution for registry-1.docker.io
log "Testing DNS resolution for registry-1.docker.io" "{\"test\":\"dns_resolution\"}" "A"
if nslookup registry-1.docker.io > /dev/null 2>&1; then
    DNS_RESULT=$(nslookup registry-1.docker.io 2>&1 | head -5)
    log "DNS resolution SUCCESS" "{\"result\":\"$(echo $DNS_RESULT | tr '\n' ' ')\"}" "A"
else
    DNS_ERROR=$(nslookup registry-1.docker.io 2>&1)
    log "DNS resolution FAILED" "{\"error\":\"$(echo $DNS_ERROR | tr '\n' ' ')\"}" "A"
fi

# Test 2: Check system DNS resolver
log "Checking system DNS resolver" "{\"test\":\"system_dns\"}" "A"
if [ -f /etc/resolv.conf ]; then
    RESOLV_CONTENT=$(cat /etc/resolv.conf | grep -v '^#' | grep -v '^$')
    log "resolv.conf content" "{\"content\":\"$(echo $RESOLV_CONTENT | tr '\n' ' ')\"}" "A"
fi

# Test 3: Test with different DNS servers
log "Testing with Google DNS (8.8.8.8)" "{\"test\":\"alternate_dns\"}" "B"
if nslookup registry-1.docker.io 8.8.8.8 > /dev/null 2>&1; then
    log "Google DNS resolution SUCCESS" "{\"dns_server\":\"8.8.8.8\"}" "B"
else
    log "Google DNS resolution FAILED" "{\"dns_server\":\"8.8.8.8\"}" "B"
fi

# Test 4: Network connectivity to Docker Hub
log "Testing network connectivity to Docker Hub" "{\"test\":\"network_connectivity\"}" "C"
if curl -s --max-time 5 https://registry-1.docker.io/v2/ > /dev/null 2>&1; then
    log "Docker Hub connectivity SUCCESS" "{\"url\":\"https://registry-1.docker.io/v2/\"}" "C"
else
    CURL_ERROR=$(curl -s --max-time 5 https://registry-1.docker.io/v2/ 2>&1 | head -3)
    log "Docker Hub connectivity FAILED" "{\"error\":\"$(echo $CURL_ERROR | tr '\n' ' ')\"}" "C"
fi

# Test 5: Docker daemon status
log "Checking Docker daemon status" "{\"test\":\"docker_daemon\"}" "D"
if docker info > /dev/null 2>&1; then
    DOCKER_INFO=$(docker info 2>&1 | grep -E "(Server Version|Operating System|Kernel Version)" | head -3)
    log "Docker daemon is running" "{\"info\":\"$(echo $DOCKER_INFO | tr '\n' ' ')\"}" "D"
else
    DOCKER_ERROR=$(docker info 2>&1 | head -3)
    log "Docker daemon check FAILED" "{\"error\":\"$(echo $DOCKER_ERROR | tr '\n' ' ')\"}" "D"
fi

# Test 6: Docker DNS configuration
log "Checking Docker DNS configuration" "{\"test\":\"docker_dns_config\"}" "D"
if [ -f /etc/docker/daemon.json ]; then
    DAEMON_JSON=$(cat /etc/docker/daemon.json 2>/dev/null)
    log "Docker daemon.json found" "{\"content\":\"$DAEMON_JSON\"}" "D"
else
    log "Docker daemon.json not found" "{\"path\":\"/etc/docker/daemon.json\"}" "D"
fi

# Test 7: Check systemd-resolved status
log "Checking systemd-resolved status" "{\"test\":\"systemd_resolved\"}" "A"
if systemctl is-active --quiet systemd-resolved 2>/dev/null; then
    RESOLVED_STATUS=$(systemctl status systemd-resolved 2>&1 | head -5)
    log "systemd-resolved is active" "{\"status\":\"$(echo $RESOLVED_STATUS | tr '\n' ' ')\"}" "A"
else
    log "systemd-resolved check" "{\"note\":\"systemctl may not be available or service not running\"}" "A"
fi

# Test 8: Test Docker pull
log "Testing Docker pull (metadata fetch)" "{\"test\":\"docker_pull_test\"}" "E"
DOCKER_PULL_OUTPUT=$(timeout 10 docker pull python:3.12 2>&1 | head -5)
if echo "$DOCKER_PULL_OUTPUT" | grep -q "error\|failed\|misbehaving"; then
    log "Docker pull test FAILED" "{\"output\":\"$(echo $DOCKER_PULL_OUTPUT | tr '\n' ' ')\"}" "E"
else
    log "Docker pull test SUCCESS" "{\"output\":\"$(echo $DOCKER_PULL_OUTPUT | tr '\n' ' ' | head -c 200)\"}" "E"
fi

# Test 9: Check Docker daemon DNS configuration from docker info
log "Checking Docker daemon DNS from docker info" "{\"test\":\"docker_info_dns\"}" "D"
DOCKER_DNS_INFO=$(docker info 2>&1 | grep -i "dns" | head -5)
if [ -n "$DOCKER_DNS_INFO" ]; then
    log "Docker daemon DNS info found" "{\"dns_info\":\"$(echo $DOCKER_DNS_INFO | tr '\n' ' ')\"}" "D"
else
    log "No DNS info in docker info (may use system default)" "{}" "D"
fi

# Test 10: Test BuildKit DNS resolution (simulate build context)
log "Testing BuildKit DNS resolution" "{\"test\":\"buildkit_dns\"}" "F"
BUILDKIT_TEST=$(DOCKER_BUILDKIT=1 docker buildx du 2>&1 | head -3)
log "BuildKit status check" "{\"output\":\"$(echo $BUILDKIT_TEST | tr '\n' ' ')\"}" "F"

# Test 11: Check if daemon.json DNS is properly configured
log "Checking daemon.json DNS configuration" "{\"test\":\"daemon_json_dns\"}" "D"
if [ -f /etc/docker/daemon.json ]; then
    DAEMON_DNS=$(cat /etc/docker/daemon.json 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); print(','.join(d.get('dns', [])))" 2>/dev/null)
    if [ -n "$DAEMON_DNS" ]; then
        log "daemon.json has DNS configured" "{\"dns_servers\":\"$DAEMON_DNS\"}" "D"
    else
        log "daemon.json exists but no DNS configured" "{}" "D"
    fi
else
    log "daemon.json missing - Docker will use system DNS" "{}" "D"
fi

echo ""
echo "=== Diagnostic Complete ==="
echo "Check debug.log for detailed results"

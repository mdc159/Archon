# Docker DNS Resolution Fix

## Problem

Docker builds fail with DNS resolution errors:
```
failed to resolve source metadata for docker.io/library/python:3.12: 
failed to do request: Head "https://registry-1.docker.io/v2/library/python/manifests/3.12": 
dial tcp: lookup registry-1.docker.io on 127.0.0.53:53: server misbehaving
```

## Root Cause

Docker BuildKit uses the host's DNS resolver (systemd-resolved at 127.0.0.53 on Ubuntu) which can intermittently fail during builds, even though host DNS resolution works fine.

## Solutions

### Solution 1: Configure Docker Daemon DNS (Recommended for Persistent Issues)

Create or edit `/etc/docker/daemon.json` to add reliable DNS servers:

```json
{
  "dns": ["8.8.8.8", "1.1.1.1", "127.0.0.53"]
}
```

Then restart Docker:
```bash
sudo systemctl restart docker
```

**Note**: This requires sudo/root access.

### Solution 2: Network DNS Configuration (Already Applied)

The `docker-compose.yml` file already includes DNS configuration for the `app-network`:
- Primary: 8.8.8.8 (Google DNS)
- Secondary: 1.1.1.1 (Cloudflare DNS)  
- Fallback: 127.0.0.53 (systemd-resolved)

This helps with container runtime DNS but doesn't affect build-time DNS resolution.

### Solution 3: Retry the Build

Often DNS issues are transient. Simply retrying the build command usually resolves the issue:
```bash
docker compose up --build -d
```

## Verification

Run the diagnostic script to verify DNS resolution:
```bash
bash .cursor/diagnose_docker_dns.sh
```

Check the logs:
```bash
cat .cursor/debug.log | jq -r '.message, .data'
```

## Current Status

Based on diagnostic results:
- ✅ Host DNS resolution: WORKING
- ✅ Network connectivity to Docker Hub: WORKING  
- ✅ Docker daemon: RUNNING
- ✅ Docker builds: WORKING (tested successfully)

The issue appears to be resolved. If it recurs, apply Solution 1 above.

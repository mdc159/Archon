# Fix Docker DNS Resolution Issues

## Problem
Docker builds intermittently fail with DNS resolution errors:
```
failed to resolve source metadata for docker.io/library/python:3.12: 
dial tcp: lookup registry-1.docker.io on 127.0.0.53:53: server misbehaving
```

## Root Cause
Docker daemon doesn't have reliable DNS servers configured. When systemd-resolved (127.0.0.53) has issues, Docker builds fail.

## Solution: Configure Docker Daemon DNS

### Option 1: Run the automated fix script (requires sudo)

```bash
sudo bash .cursor/fix_docker_dns.sh
```

This script will:
- Create `/etc/docker/daemon.json` with reliable DNS servers
- Backup existing config if present
- Restart Docker daemon
- Verify the fix

### Option 2: Manual configuration

1. **Create or edit `/etc/docker/daemon.json`:**

```bash
sudo mkdir -p /etc/docker
sudo nano /etc/docker/daemon.json
```

2. **Add this configuration:**

```json
{
  "dns": ["8.8.8.8", "1.1.1.1", "127.0.0.53"]
}
```

3. **Restart Docker:**

```bash
sudo systemctl restart docker
```

4. **Verify:**

```bash
docker info | grep -i dns
docker compose up --build -d
```

## DNS Servers Explained

- **8.8.8.8** - Google DNS (primary, highly reliable)
- **1.1.1.1** - Cloudflare DNS (secondary, fast)
- **127.0.0.53** - systemd-resolved (fallback for local resolution)

## Verification

After applying the fix, run diagnostics:

```bash
bash .cursor/diagnose_docker_dns.sh
cat .cursor/debug.log | jq -r '.message, .data' | grep -A 1 "daemon.json"
```

You should see: `"daemon.json has DNS configured"` with the DNS servers listed.

## Why This Works

Docker BuildKit uses the Docker daemon's DNS configuration during image pulls. By configuring reliable DNS servers at the daemon level, we prevent intermittent failures when systemd-resolved has issues.

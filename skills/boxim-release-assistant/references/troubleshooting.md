# Troubleshooting Guide

Common deployment failures and fixes for boxim.

## 1. im-web build fails with "digital envelope routines" error

**Symptom:** `Error: error:0308010C:digital envelope routines::unsupported`

**Cause:** Node 17+ uses OpenSSL 3.0, incompatible with old webpack crypto.

**Fix:**
```bash
# Windows PowerShell
$env:NODE_OPTIONS="--openssl-legacy-provider"
npm run build

# Linux / macOS
export NODE_OPTIONS=--openssl-legacy-provider
npm run build
```

## 2. WebSocket connection fails after deploy

**Symptom:** Frontend shows "连接断开" or WS handshake returns 400.

**Checklist:**
1. `systemctl status im-server` — is it running?
2. `journalctl -u im-server --lines 50` — look for port bind errors
3. Nginx config: verify `Upgrade` and `Connection` headers are set
4. `nginx -t` — test config syntax
5. Firewall: `ufw status` — ensure port 80/443 open
6. Test directly: `wscat -c ws://127.0.0.1:8878/ws` (bypasses Nginx)

**Fix:** If im-server fails to bind, check for orphaned Java processes:
```bash
ps aux | grep im-server
kill -9 <pid>
systemctl start im-server
```

## 3. im-platform won't start — port already in use

**Symptom:** `Web server failed to start. Port 8888 was already in use.`

**Fix:**
```bash
lsof -i :8888
kill -9 $(lsof -t -i :8888)
systemctl restart im-platform
```

## 4. H5 page blank after deploy

**Symptom:** h5.lexiangim.com shows blank white page.

**Common causes:**
- Wrong deploy path: files must go to `/opt/boxim/h5-ui/h5/`, not `/opt/boxim/h5-ui/`
- Missing `index.html`: verify `ls /opt/boxim/h5-ui/h5/index.html`
- Asset paths: uni-app build uses relative paths by default; check `manifest.json` → `h5.router.base`
- Nginx root points to wrong directory

**Fix:**
```bash
ls -la /opt/boxim/h5-ui/h5/
# Should contain index.html, static/, etc.
```

## 5. Database connection errors after deploy

**Symptom:** `Communications link failure` or `HikariPool-1 - Exception during pool initialization.`

**Checklist:**
1. `systemctl status mysql` — MySQL running?
2. `mysql -u root -p -e "SHOW DATABASES;"` — credentials correct?
3. Check `/opt/boxim/config/application-prod.yml` (or wherever config lives) for correct JDBC URL
4. `netstat -tlnp | grep 3306` — MySQL listening?

## 6. OOM (Out of Memory) on 2C4G server

**Symptom:** Service killed by OOM killer, `dmesg | grep -i oom` shows Java process.

**Fix:**
- Reduce heap sizes in systemd units (see systemd-units.md)
- Add swap:
```bash
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```
- Monitor: `free -h`, `top` (sort by M)

## 7. Health check script not running

**Symptom:** No Telegram alerts, cron not executing.

**Fix:**
```bash
crontab -l
# Should contain: * * * * * /bin/bash /opt/boxim/tg-bot/health_check.sh >> /var/log/boxim-health.log 2>&1
chmod +x /opt/boxim/tg-bot/health_check.sh
bash -x /opt/boxim/tg-bot/health_check.sh  # debug run
```

## 8. Rollback doesn't restore frontend

**Symptom:** After rollback, frontend still shows new version.

**Cause:** Browser cache or Nginx cache.

**Fix:**
```bash
# Hard reload Nginx
systemctl reload nginx
# Clear any Nginx cache if configured
rm -rf /var/cache/nginx/*
# Users need Ctrl+Shift+R to bypass browser cache
```

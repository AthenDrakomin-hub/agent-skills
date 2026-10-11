---
name: boxim-release-assistant
description: Use when the user needs to build, deploy, release, health-check, or roll back the boxim instant messaging project across im-web (Vue2), im-uniapp (Vue3 H5), and Java backend (im-platform / im-server / im-admin). Triggers on "发版", "部署 boxim", "redeploy", "健康检查", "回滚", "restart im-platform".
license: MIT
compatibility: Requires SSH access to the production server, local Node.js + Maven build environment, and scp. Targets Ubuntu 24.04 + Java 21 runtime.
metadata:
  author: AthenDrakomin-hub
  version: "1.0.0"
  category: devops
---

# BoxIM Release Assistant

## Role
You are a DevOps release engineer for the boxim instant messaging system. You execute safe, verifiable deployments across three frontend bundles and three Java backend services, with mandatory health checks before and after each release, and one-command rollback when checks fail.

## Architecture Overview
| Component | Tech | Build | Deploy Target | Port |
|---|---|---|---|---|
| im-web | Vue2 + ElementUI | `npm run build` (needs `NODE_OPTIONS=--openssl-legacy-provider`) | `/opt/boxim/web-ui/` | 80 (Nginx) |
| im-uniapp H5 | Vue3 + UniApp 1.0.4 | HBuilderX build → `dist/build/h5/` | `/opt/boxim/h5-ui/h5/` | 80 (Nginx) |
| im-pc | Electron shell | local packager | manual install | — |
| im-platform | Java / Spring Boot | `mvn clean package` | `/opt/boxim/im-platform.jar` | 8888 |
| im-server | Java / Netty WS | `mvn clean package` | `/opt/boxim/im-server.jar` | 8878 (WS) |
| im-admin | Java / Spring Boot | `mvn clean package` | `/opt/boxim/im-admin.jar` | 8889 |

All backend services are managed by systemd. Production server: root@45.77.31.155 (Vultr Tokyo, 2C4G, Ubuntu 24.04).

## Objectives
- Build frontend bundles locally and backend jars on the server (or locally per user choice)
- Backup current artifacts before overwriting
- Deploy with zero/minimal downtime, restart services in dependency order
- Run health checks (HTTP + WS connectivity) after each restart
- Auto-rollback if health checks fail within the grace window
- Produce a release report with timestamps, commit SHA, and check results

## Release Workflow

### Phase 0 — Pre-flight Checks
1. Confirm the current branch and latest commit: `git log -1 --oneline`.
2. Verify no uncommitted changes that should be included: `git status --short`.
3. Confirm SSH connectivity: `ssh -o ConnectTimeout=5 root@45.77.31.155 'echo ok'`.
4. Record current running versions: `systemctl status im-platform im-server im-admin --no-pager`.
5. Ask the user to confirm the release scope (frontend only / backend only / full stack) before proceeding.

### Phase 1 — Backup
On the server, timestamp and copy current artifacts:
```bash
TS=$(date +%Y%m%d-%H%M%S)
mkdir -p /root/boxim-backup-$TS
cp /opt/boxim/im-platform.jar /root/boxim-backup-$TS/
cp /opt/boxim/im-server.jar /root/boxim-backup-$TS/
cp /opt/boxim/im-admin.jar /root/boxim-backup-$TS/
cp -r /opt/boxim/web-ui /root/boxim-backup-$TS/web-ui
cp -r /opt/boxim/h5-ui /root/boxim-backup-$TS/h5-ui
echo $TS > /root/boxim-backup-$TS/TIMESTAMP
```

### Phase 2 — Build
**Frontend (local):**
```bash
# im-web
cd im-web
$env:NODE_OPTIONS="--openssl-legacy-provider"
npm run build
# output: dist/

# im-uniapp H5 — build via HBuilderX, output dist/build/h5/
```

**Backend (on server, preferred):**
```bash
cd /root/boxim
git pull origin main
cd box-im
mvn clean package -DskipTests
# jars appear in box-im/im-platform/target/, etc.
```

### Phase 3 — Deploy
**Frontend:**
```bash
scp -r im-web/dist/* root@45.77.31.155:/opt/boxim/web-ui/
scp -r im-uniapp/dist/build/h5/* root@45.77.31.155:/opt/boxim/h5-ui/h5/
ssh root@45.77.31.155 'nginx -t && systemctl reload nginx'
```

**Backend (order: platform → server → admin):**
```bash
ssh root@45.77.31.155 '
  cp /root/boxim/box-im/im-platform/target/im-platform.jar /opt/boxim/im-platform.jar
  systemctl restart im-platform
  sleep 5
  cp /root/boxim/box-im/im-server/target/im-server.jar /opt/boxim/im-server.jar
  systemctl restart im-server
  sleep 3
  cp /root/boxim/box-im/im-admin/target/im-admin.jar /opt/boxim/im-admin.jar
  systemctl restart im-admin
'
```

### Phase 4 — Health Checks
Run the production health script and verify each endpoint:
```bash
ssh root@45.77.31.155 'bash /opt/boxim/tg-bot/health_check.sh'
```
Manual verification:
- `curl -s -o /dev/null -w "%{http_code}" https://web.lexiangim.com/` → 200
- `curl -s -o /dev/null -w "%{http_code}" https://admin.lexiangim.com/` → 200
- WebSocket: `wscat -c wss://im.lexiangim.com/ws` → connects
- `systemctl is-active im-platform im-server im-admin` → all `active`

If any check fails, proceed immediately to Phase 5 (rollback).

### Phase 5 — Rollback (conditional)
```bash
ssh root@45.77.31.155 '
  BK=/root/boxim-backup-$(ls -t /root/ | grep boxim-backup | head -1 | sed "s/boxim-backup-//")
  cp $BK/im-platform.jar /opt/boxim/ && systemctl restart im-platform
  cp $BK/im-server.jar /opt/boxim/ && systemctl restart im-server
  cp $BK/im-admin.jar /opt/boxim/ && systemctl restart im-admin
  rm -rf /opt/boxim/web-ui/* && cp -r $BK/web-ui/* /opt/boxim/web-ui/
  rm -rf /opt/boxim/h5-ui/h5/* && cp -r $BK/h5-ui/h5/* /opt/boxim/h5-ui/h5/
  systemctl reload nginx
'
```
Re-run health checks. Report the rollback reason and restored timestamp.

### Phase 6 — Release Report
Output a structured summary:
```
## Release Report — {date}
- Commit: {sha}
- Scope: {frontend / backend / full}
- Backup: /root/boxim-backup-{ts}/
- im-platform: {restarted / skipped} — health {pass/fail}
- im-server: {restarted / skipped} — health {pass/fail}
- im-admin: {restarted / skipped} — health {pass/fail}
- web-ui: {deployed / skipped} — HTTP {code}
- h5-ui: {deployed / skipped} — HTTP {code}
- Rollback: {none / executed}
- Duration: {mm:ss}
```

## Guidelines
1. Never deploy without a backup. The backup directory is the rollback source of truth.
2. Backend restart order matters: im-platform first (API), then im-server (WS depends on platform), then im-admin.
3. Always run `nginx -t` before reloading Nginx; a bad config will take all frontends down.
4. The `NODE_OPTIONS=--openssl-legacy-provider` flag is mandatory for im-web builds on Node 17+.
5. Do not delete source code on the server after build — the one-click `redeploy.sh` handles cleanup.
6. If the user provides the one-click script path, prefer `bash /opt/boxim/redeploy.sh` for backend-only releases, but still run manual health checks afterward.
7. Never expose SSH keys, passwords, or `.env` contents in the release report or logs.

## Quick Commands Reference
| Action | Command |
|---|---|
| One-click backend redeploy | `ssh root@45.77.31.155 'bash /opt/boxim/redeploy.sh'` |
| Check service status | `ssh root@45.77.31.155 'systemctl status im-platform im-server im-admin --no-pager'` |
| Tail platform logs | `ssh root@45.77.31.155 'journalctl -u im-platform -f --lines 50'` |
| Health check | `ssh root@45.77.31.155 'bash /opt/boxim/tg-bot/health_check.sh'` |
| Disk usage | `ssh root@45.77.31.155 'df -h / && du -sh /opt/boxim/*'` |

## References
- `references/nginx-config.md` — production Nginx server block templates
- `references/systemd-units.md` — systemd service file examples
- `references/troubleshooting.md` — common deployment failures and fixes

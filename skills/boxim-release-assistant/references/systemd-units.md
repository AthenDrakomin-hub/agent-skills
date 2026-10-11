# systemd Unit Files

Place in `/etc/systemd/system/`. Run `systemctl daemon-reload` after editing.

## im-platform.service
```ini
[Unit]
Description=BoxIM Platform API Service
After=network.target mysql.service redis.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/boxim
ExecStart=/usr/bin/java -Xms256m -Xmx768m -jar /opt/boxim/im-platform.jar
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
Environment="SPRING_PROFILES_ACTIVE=prod"

[Install]
WantedBy=multi-user.target
```

## im-server.service (WebSocket)
```ini
[Unit]
Description=BoxIM WebSocket Server
After=network.target im-platform.service
Requires=im-platform.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/boxim
ExecStart=/usr/bin/java -Xms128m -Xmx512m -jar /opt/boxim/im-server.jar
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

## im-admin.service
```ini
[Unit]
Description=BoxIM Admin Service
After=network.target im-platform.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/boxim
ExecStart=/usr/bin/java -Xms128m -Xmx256m -jar /opt/boxim/im-admin.jar
Restart=on-failure
RestartSec=10
StandardOutput=journal

[Install]
WantedBy=multi-user.target
```

## Common Commands
```bash
systemctl daemon-reload
systemctl enable im-platform im-server im-admin
systemctl start im-platform && sleep 5 && systemctl start im-server && systemctl start im-admin
systemctl status im-platform im-server im-admin --no-pager
journalctl -u im-platform -f --lines 100
```

## JVM Tuning Notes
- Server has 4GB RAM total. Allocate: platform 768m, server 512m, admin 256m = ~1.5GB heap, leaving room for OS, MySQL, Redis, Nginx.
- Use `-XX:+UseG1GC` for JDK 21 (default).
- Add `-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/opt/boxim/dumps/` for post-mortem analysis.

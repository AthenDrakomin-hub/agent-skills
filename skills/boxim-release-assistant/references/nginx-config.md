# Nginx Configuration Reference

Production Nginx server blocks for boxim. Place in `/etc/nginx/sites-available/` and symlink to `sites-enabled/`.

## im-web (Vue2 SPA)
```nginx
server {
    listen 80;
    server_name web.lexiangim.com;

    root /opt/boxim/web-ui;
    index index.html;

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Static assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API proxy to im-platform
    location /api/ {
        proxy_pass http://127.0.0.1:8888;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 60s;
    }

    client_max_body_size 50m;
}
```

## im-uniapp H5
```nginx
server {
    listen 80;
    server_name h5.lexiangim.com;

    root /opt/boxim/h5-ui/h5;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8888;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## WebSocket (im-server)
```nginx
server {
    listen 80;
    server_name im.lexiangim.com;

    location /ws {
        proxy_pass http://127.0.0.1:8878;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
}
```

## im-admin
```nginx
server {
    listen 80;
    server_name admin.lexiangim.com;

    location / {
        proxy_pass http://127.0.0.1:8889;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        client_max_body_size 20m;
    }
}
```

## HTTPS (certbot)
After obtaining certificates with certbot, add to each server block:
```nginx
listen 443 ssl;
ssl_certificate /etc/letsencrypt/live/<domain>/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/<domain>/privkey.pem;
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
```

## Verification
```bash
nginx -t                    # test config
systemctl reload nginx      # zero-downtime reload
tail -f /var/log/nginx/error.log
```

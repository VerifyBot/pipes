# Production

While developing, use ngrok to allow testing the wildcard subdomain. <br>

```shell
ngrok tcp 6969
```

## Server

### DNS Setup

Configure A records for the subdomain and the wildcard subdomain.
```
A   m.nirush.me     directs to  167.99.210.149
A   *.m.nirush.me   directs to  167.99.210.149
```

Validate via `host m.nirush.me` and `host test.m.nirush.me`

### Machine Setup (Ubuntu)

open ports (22, 80, 443)

```shell
ufw enable
ufw allow 22
ufw allow 80/tcp
ufw allow 443/tcp
```

create a certificate for the .m subdomain

```shell
snap install --classic certbot
ln -s /snap/bin/certbot /usr/bin/certbot
certbot certonly --standalone
```

create a certificate for the wildcard (*.m) subdomain <br>
👉 Reference: https://www.digitalocean.com/community/tutorials/how-to-create-let-s-encrypt-wildcard-certificates-with-certbot <br>
👉 Get DIGITAL_OCEAN_TOKEN: https://cloud.digitalocean.com/settings/api/tokens

```shell
apt install python3-certbot-dns-digitalocean
vim ~/certbot-creds.ini
# dns_digitalocean_token = DIGITAL_OCEAN_TOKEN
chmod 600 ~/certbot-creds.ini
sudo certbot certonly --dns-digitalocean --dns-digitalocean-credentials ~/certbot-creds.ini -d '*.m.nirush.me'
```

nginx configuration

```shell
apt install nginx
apt install nginx-extras
vim /etc/nginx/sites-available/m.nirush.me
```

Inside the file:
```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name m.nirush.me *.m.nirush.me;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name m.nirush.me;

    ssl_certificate /etc/letsencrypt/live/m.nirush.me-0001/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/m.nirush.me-0001/privkey.pem;

    location / {
        proxy_pass http://localhost:6969;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl;
    server_name *.m.nirush.me;

    ssl_certificate /etc/letsencrypt/live/m.nirush.me/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/m.nirush.me/privkey.pem;

    location / {
        proxy_pass http://localhost:6969;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

reload nginx

```shell
nginx -t  # test
systemctl reload nginx
```

### Python Setup

alias python
```shell
vim ~/.bashrc, and add :

- alias python='python3'
- alias pip='python3 -m pip'
  source ~/.bashrc
```

install python, pip and venv
```shell
apt install python3 python3-pip python3-venv -y
```

use this to create a virtual environment
```shell
python -m venv .venv
source .venv/bin/activate
```

run the server
```shell
sanic server:app -p 6969
```

## Client

```shell
npm run build

firebase init
firebase deploy
```
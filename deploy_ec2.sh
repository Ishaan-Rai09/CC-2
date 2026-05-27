#!/bin/bash

set -euo pipefail

APP_ROOT="${HOME}/smart-notes"
BACKEND_DIR="${APP_ROOT}/backend"
FRONTEND_DIR="${APP_ROOT}/frontend"
ENV_FILE="${BACKEND_DIR}/.env"

echo "====================================================="
echo "Starting Smart Notes deployment on AWS EC2"
echo "====================================================="

if [ ! -d "${APP_ROOT}" ]; then
    echo "Expected project directory at ${APP_ROOT}"
    exit 1
fi

echo "Installing system packages..."
sudo apt update
sudo apt install -y python3-pip python3-venv nginx curl git ca-certificates

if ! command -v node >/dev/null 2>&1; then
    echo "Installing Node.js 20..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt install -y nodejs
fi

echo "Preparing backend environment..."
cd "${BACKEND_DIR}"
rm -rf venv
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

if [ ! -f "${ENV_FILE}" ]; then
    cp .env.example .env
fi

python - <<'PY'
from pathlib import Path
import secrets

env_path = Path(".env")
lines = env_path.read_text().splitlines()

def set_or_add(key: str, value: str) -> None:
    prefix = f"{key}="
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines[index] = f'{key}="{value}"'
            return
    lines.append(f'{key}="{value}"')

secret = secrets.token_urlsafe(48)
set_or_add("DEBUG", "False")
set_or_add("SECRET_KEY", secret)
set_or_add("ANALYTICS_ENGINE", "aws_glue")

env_path.write_text("\n".join(lines) + "\n")
PY

echo "Starting backend with PM2..."
sudo npm install -g pm2
pm2 delete smart-notes-api >/dev/null 2>&1 || true
pm2 start "bash -lc 'cd ${BACKEND_DIR} && source venv/bin/activate && uvicorn app.main:app --host 127.0.0.1 --port 8000'" --name "smart-notes-api"
pm2 save
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u ubuntu --hp /home/ubuntu || true

echo "Building frontend..."
cd "${FRONTEND_DIR}"
npm install
VITE_API_URL=/api npm run build

echo "Publishing frontend..."
sudo rm -rf /var/www/html/*
sudo cp -r dist/* /var/www/html/

echo "Writing Nginx configuration..."
sudo tee /etc/nginx/sites-available/default >/dev/null <<'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    root /var/www/html;
    index index.html index.htm;

    server_name _;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    location /uploads/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo systemctl restart nginx

echo "====================================================="
echo "Deployment complete"
echo "====================================================="
echo "App URL: http://<your-ec2-public-ip>"
echo "Backend env file: ${ENV_FILE}"
echo "If you want AWS Glue analytics, add AWS credentials, bucket, and job name to ${ENV_FILE}, then run:"
echo "pm2 restart smart-notes-api"

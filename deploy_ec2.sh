#!/bin/bash
# ==============================================================================
# AWS EC2 DEPLOYMENT SCRIPT FOR SMART NOTES (Ubuntu 24.04 LTS)
# Run this script ON your EC2 instance to fully deploy the project.
# ==============================================================================

set -e # Exit on any error

echo "====================================================="
echo "🚀 Starting Smart Notes Deployment on AWS EC2..."
echo "====================================================="

# 1. Update system and install dependencies
echo "📦 Installing system dependencies (Python, Node.js, Nginx, Java for PySpark)..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx curl git default-jre

# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 2. Setup Backend (FastAPI + PySpark)
echo "🐍 Setting up Python Backend..."
cd ~/smart-notes/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Ensure .env exists (User must fill this out manually later)
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Created .env from example. Please edit it with your AWS credentials later!"
fi

# 3. Setup PM2 to run FastAPI in the background
echo "⚙️  Configuring PM2 for backend process management..."
sudo npm install -g pm2
pm2 start "uvicorn app.main:app --host 127.0.0.1 --port 8000" --name "smart-notes-api"
pm2 save
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u ubuntu --hp /home/ubuntu || true

# 4. Build Frontend (React)
echo "⚛️  Building React Frontend..."
cd ~/smart-notes/frontend
npm install
npm run build

# 5. Configure Nginx (Web Server)
echo "🌐 Configuring Nginx..."
sudo cp -r dist/* /var/www/html/

# Create Nginx config
sudo bash -c 'cat > /etc/nginx/sites-available/default <<EOF
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    root /var/www/html;
    index index.html index.htm index.nginx-debian.html;

    server_name _;

    # Serve React Frontend
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # Proxy API requests to FastAPI
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Increase timeout for large file uploads
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
EOF'

# Restart Nginx
sudo systemctl restart nginx

echo "====================================================="
echo "✅ Deployment Complete!"
echo "====================================================="
echo "Your app is now live. Access it via your EC2 Public IPv4 address."
echo "Don't forget to edit your AWS credentials: nano ~/smart-notes/backend/.env"
echo "Then restart the API: pm2 restart smart-notes-api"

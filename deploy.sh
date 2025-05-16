#!/bin/bash

# Update system
sudo yum update -y

# Install Python 3.9 and development tools
sudo yum install -y python3.9 python3.9-devel gcc

# Install nginx
sudo yum install -y nginx

# Create application directory
sudo mkdir -p /var/www/ubbank
sudo chown -R ec2-user:ec2-user /var/www/ubbank

# Create and activate virtual environment
python3.9 -m venv /var/www/ubbank/venv
source /var/www/ubbank/venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service file
sudo tee /etc/systemd/system/ubbank.service << EOF
[Unit]
Description=UBBank FastAPI Application
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/var/www/ubbank
Environment="PATH=/var/www/ubbank/venv/bin"
ExecStart=/var/www/ubbank/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
sudo tee /etc/nginx/conf.d/ubbank.conf << EOF
server {
    listen 80;
    server_name _;  # Replace with your domain name when you have one

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias /var/www/ubbank/static;
    }
}
EOF

# Start and enable services
sudo systemctl daemon-reload
sudo systemctl enable ubbank
sudo systemctl start ubbank
sudo systemctl enable nginx
sudo systemctl start nginx

# Configure firewall
sudo yum install -y firewalld
sudo systemctl enable firewalld
sudo systemctl start firewalld
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

echo "Deployment completed! Check the status with:"
echo "sudo systemctl status ubbank"
echo "sudo systemctl status nginx" 
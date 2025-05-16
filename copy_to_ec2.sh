#!/bin/bash

# EC2 instance details
EC2_HOST="ec2-3-250-182-141.eu-west-1.compute.amazonaws.com"
EC2_USER="ec2-user"
KEY_FILE="ubank.pem"

# Create a temporary directory for deployment
mkdir -p deploy_temp
cp -r backend frontend requirements.txt deploy.sh docker-compose.yml deploy_temp/
cp -r nginx deploy_temp/
cp ubank.pem deploy_temp/

# Copy files to EC2
scp -i "$KEY_FILE" -r deploy_temp/* "$EC2_USER@$EC2_HOST:/var/www/ubbank/"

# Clean up
rm -rf deploy_temp

echo "Files copied to EC2. Now SSH into the instance and run deploy.sh:"
echo "ssh -i ubank.pem ec2-user@$EC2_HOST"
echo "cd /var/www/ubbank && chmod +x deploy.sh && ./deploy.sh"
echo ""
echo "After deployment, you'll need to:"
echo "1. Edit /var/www/ubbank/.env and set your domain name"
echo "2. Edit /var/www/ubbank/init-letsencrypt.sh and set your domain and email"
echo "3. Run: docker-compose up -d"
echo "4. Execute: ./init-letsencrypt.sh" 
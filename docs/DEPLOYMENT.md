# AWS Academy Learner Lab - EC2 Deployment Guide

This guide provides exact instructions for deploying the Smart Notes app (with SQLite and PySpark) onto a single AWS EC2 instance, accessed directly via its Public IPv4 address.

## Step 1: Launch an EC2 Instance

1. Go to AWS Console -> **EC2** -> **Launch Instance**.
2. **Name**: `smart-notes-server`
3. **OS**: Ubuntu 24.04 LTS
4. **Instance Type**: **`t3.medium`** (CRITICAL: PySpark requires at least 4GB of RAM. Do NOT use `t2.micro` or it will crash).
5. **Key Pair**: Create a new key pair (`smart-notes-key.pem`) and download it to your computer.
6. **Network Settings**: 
   - Allow SSH traffic from Anywhere
   - Allow HTTP traffic from the internet
   - Allow HTTPS traffic from the internet
7. **Storage**: 15 GB gp3.
8. Click **Launch instance**.

## Step 2: Connect to the Instance

Open your local terminal (Command Prompt, PowerShell, or Mac Terminal) where you downloaded your `.pem` key:

```bash
# Set secure permissions on the key (Mac/Linux only)
chmod 400 smart-notes-key.pem

# Connect to the instance
ssh -i "smart-notes-key.pem" ubuntu@<YOUR-EC2-PUBLIC-IP>
```

## Step 3: Download Your Code

Once inside the EC2 terminal, you need to get your code onto the server. You can clone your GitHub repository:

```bash
git clone <YOUR-GITHUB-REPO-URL> smart-notes
cd smart-notes
```

*(Note: If you haven't uploaded to GitHub, you will need to do that first, or use `scp` to copy your files over).*

## Step 4: Run the Automated Deployment Script

I have created an automated deployment script `deploy_ec2.sh` that installs Java (for PySpark), Node.js, Nginx, Python, and configures PM2 to keep the server running.

Run the following commands:

```bash
# Make the script executable
chmod +x deploy_ec2.sh

# Run the deployment
./deploy_ec2.sh
```

## Step 5: Configure AWS Credentials

The deployment script successfully built the app, but you must provide your Learner Lab AWS credentials so S3 works.

```bash
nano ~/smart-notes/backend/.env
```

Paste your temporary AWS Academy credentials:
```env
AWS_ACCESS_KEY_ID="ASIA..."
AWS_SECRET_ACCESS_KEY="..."
AWS_SESSION_TOKEN="..."
```

Save and exit `nano` (`Ctrl+O`, `Enter`, `Ctrl+X`).

## Step 6: Restart the API

Apply the new credentials by restarting the FastAPI server:

```bash
pm2 restart smart-notes-api
```

## Step 7: Access the App

Open your web browser and navigate to your EC2 instance's **Public IPv4 address**:
`http://<YOUR-EC2-PUBLIC-IP>`

Your application is now live on the internet! 

*(Remember to stop your EC2 instance when not in use to save your $50 Learner Lab credits).*

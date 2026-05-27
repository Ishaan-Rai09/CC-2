# AWS Academy Learner Lab EC2 Deployment Guide

This project is best deployed in AWS Academy Learner Lab as a single EC2 instance.
That fits the app's current architecture:

- React frontend built as static files
- FastAPI backend behind Nginx
- SQLite database stored on the instance
- Uploaded files stored on the instance under `uploads/`
- PySpark analytics can run either locally or in AWS Glue

## Recommended AWS Setup

- Service: `EC2`
- OS: `Ubuntu 24.04 LTS`
- Instance type: `t3.small`
- Storage: `20 GB gp3`
- Security group inbound:
  - `SSH` on port `22` from your IP only
  - `HTTP` on port `80` from `0.0.0.0/0`
  - `HTTPS` on port `443` from `0.0.0.0/0` if you add a domain later

`t3.micro` may boot, but PySpark and builds are much less reliable there.

## Why EC2 Is The Right First Step

- Learner Lab commonly supports EC2 and S3, while some managed services may be restricted.
- Your app currently uses SQLite and local file storage, which makes single-instance hosting the simplest option.
- It keeps cost and moving parts low while you validate the project.

## Before You Launch

1. Push this repo to GitHub, or prepare to copy it with `scp`.
2. Make sure you can SSH with a key pair.
3. Keep in mind that if the instance is terminated, your SQLite DB and uploaded files are gone unless you back them up.

## Launch The EC2 Instance

1. Open the AWS Console.
2. Go to `EC2`.
3. Click `Launch instance`.
4. Use:
   - Name: `smart-notes-server`
   - AMI: `Ubuntu 24.04 LTS`
   - Instance type: `t3.small`
   - Storage: `20 GB gp3`
5. Create or select a key pair.
6. Configure the security group:
   - Allow `SSH` from your IP
   - Allow `HTTP` from the internet
   - Allow `HTTPS` from the internet if needed later
7. Launch the instance.

## Connect To The Server

```bash
ssh -i "smart-notes-key.pem" ubuntu@<EC2_PUBLIC_IP>
```

## Copy The Project

Using Git:

```bash
git clone <YOUR_GITHUB_REPO_URL> smart-notes
cd smart-notes
```

Or copy the project from your machine with `scp`.

## Run The Deployment Script

On the EC2 instance:

```bash
chmod +x deploy_ec2.sh
./deploy_ec2.sh
```

The script will:

- install Python, Node.js, Java, and Nginx
- create swap for PySpark stability
- create a virtual environment
- install backend dependencies
- build the frontend with `VITE_API_URL=/api`
- start FastAPI with PM2
- configure Nginx for `/`, `/api`, and `/uploads`

## Environment Variables

Edit the backend environment file:

```bash
nano ~/smart-notes/backend/.env
```

At minimum, change:

```env
SECRET_KEY="replace-with-a-long-random-secret"
DEBUG=False
```

### About AWS Credentials

Right now the repo stores uploads locally in `backend/uploads` and does not require live S3 credentials to work.

That means you can deploy immediately without:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_SESSION_TOKEN`

If you later switch the storage layer back to real S3, Learner Lab temporary credentials may expire, so instance-role-based access is better if your lab allows it.

## Open The App

Visit:

```text
http://<EC2_PUBLIC_IP>
```

## Useful Commands

Restart API:

```bash
pm2 restart smart-notes-api
```

Check API logs:

```bash
pm2 logs smart-notes-api
```

Restart Nginx:

```bash
sudo systemctl restart nginx
```

## Important Limits Of This First Deployment

- SQLite is fine for demos and coursework, but not ideal for multi-user production.
- Local uploads are lost if the instance disk is lost or the instance is rebuilt.
- Learner Lab is great for learning, but not ideal for long-term public hosting.

## Best Next Upgrade Path

Once the EC2 deployment works, the next improvements should be:

1. Move SQLite to PostgreSQL.
2. Move uploads to S3.
3. Keep analytics on AWS Glue and add stronger job/result observability.
4. Add a domain and HTTPS with Nginx + Let's Encrypt or an AWS load balancer.
5. Add automated backups.

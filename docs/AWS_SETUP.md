# AWS Setup Guide for Smart Notes

This guide explains how to set up AWS S3 for the file storage functionality, optimized for an AWS Academy Learner Lab environment.

## 1. Create an S3 Bucket

1. Log into your AWS Console.
2. Search for **S3** and click **Create bucket**.
3. **Bucket name**: e.g., `smart-notes-files-2026` (must be globally unique).
4. **Region**: e.g., `us-east-1`.
5. **Object Ownership**: ACLs disabled (recommended).
6. **Block Public Access**: 
   - Keep "Block all public access" **CHECKED**.
   - The application generates secure, temporary presigned URLs for downloads, so objects do not need to be public.
7. Click **Create bucket**.

## 2. Configure CORS (Cross-Origin Resource Sharing)

If you plan to upload files directly from the browser (presigned POSTs), you need CORS. Since our upload flows through the FastAPI backend, CORS on the bucket is optional, but recommended for future scaling.

1. Select your bucket -> **Permissions** tab.
2. Scroll to **Cross-origin resource sharing (CORS)** and click **Edit**.
3. Paste the following:
```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "PUT", "POST", "HEAD"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": []
    }
]
```

## 3. Configure IAM Credentials

### If using AWS Academy (Learner Lab):
You cannot create IAM users. Instead, you must use the temporary credentials provided in the lab environment.
1. Click **AWS Details** in the Learner Lab.
2. Click **Show** next to AWS CLI.
3. Copy the `aws_access_key_id`, `aws_secret_access_key`, and `aws_session_token`.
4. Paste these into your backend `.env` file.
*(Note: These credentials expire every few hours when the lab stops, so you will need to update your `.env` frequently during development).*

### If using a Personal AWS Account:
1. Go to **IAM** -> **Users** -> **Add users**.
2. Name the user (e.g., `smart-notes-app`).
3. Attach policies directly: Search for and select `AmazonS3FullAccess`.
4. Create the user.
5. Go to the user's **Security credentials** tab and click **Create access key**.
6. Copy the `Access Key ID` and `Secret Access Key` to your `.env` file. You do NOT need a session token.

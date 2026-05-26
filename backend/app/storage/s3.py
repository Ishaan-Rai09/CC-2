import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException
import uuid
import os
from ..config import get_settings

settings = get_settings()


def get_s3_client():
    kwargs = {
        "region_name": settings.AWS_REGION,
    }
    if settings.AWS_ACCESS_KEY_ID:
        kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
    if settings.AWS_SECRET_ACCESS_KEY:
        kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
    if settings.AWS_SESSION_TOKEN:
        kwargs["aws_session_token"] = settings.AWS_SESSION_TOKEN
    return boto3.client("s3", **kwargs)


def upload_file_to_s3(file_bytes: bytes, filename: str, content_type: str, user_id: int) -> dict:
    """Upload file to S3 and return key + presigned URL."""
    ext = os.path.splitext(filename)[1].lower()
    unique_key = f"users/{user_id}/notes/{uuid.uuid4().hex}{ext}"

    try:
        s3 = get_s3_client()
        s3.put_object(
            Bucket=settings.AWS_BUCKET_NAME,
            Key=unique_key,
            Body=file_bytes,
            ContentType=content_type,
        )
        # Generate presigned URL valid for 7 days
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.AWS_BUCKET_NAME, "Key": unique_key},
            ExpiresIn=604800,
        )
        return {"key": unique_key, "url": url}
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not configured")
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")


def delete_file_from_s3(file_key: str) -> bool:
    """Delete a file from S3."""
    try:
        s3 = get_s3_client()
        s3.delete_object(Bucket=settings.AWS_BUCKET_NAME, Key=file_key)
        return True
    except ClientError:
        return False


def generate_presigned_url(file_key: str, expiry: int = 3600) -> str:
    """Generate a fresh presigned download URL."""
    try:
        s3 = get_s3_client()
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.AWS_BUCKET_NAME, "Key": file_key},
            ExpiresIn=expiry,
        )
        return url
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Could not generate URL: {str(e)}")

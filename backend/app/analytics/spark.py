import json
import logging
import time
from collections import Counter
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from sqlalchemy.orm import Session

from ..config import get_settings
from ..notes.models import Note
from .models import AnalyticsJob

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

logger = logging.getLogger(__name__)
settings = get_settings()

JOB_STATUS_RUNNING = {"STARTING", "RUNNING", "STOPPING", "WAITING", "QUEUED"}
JOB_STATUS_SUCCESS = "SUCCEEDED"
JOB_STATUS_FAILURE = {"FAILED", "STOPPED", "TIMEOUT", "ERROR", "EXPIRED"}


def get_spark_session() -> "SparkSession":
    try:
        from pyspark.sql import SparkSession
    except ImportError as exc:
        raise RuntimeError("PySpark is not installed on this server.") from exc

    return (
        SparkSession.builder
        .appName("SmartNotesAnalytics")
        .master("local[*]")
        .config("spark.driver.memory", "512m")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )


def compute_analytics(db: Session, user_id: int) -> tuple[dict, int]:
    engine = settings.ANALYTICS_ENGINE.lower().strip()
    if engine == "aws_glue":
        return compute_analytics_via_glue(db, user_id)
    return compute_analytics_local(db, user_id), 200


def compute_analytics_local(db: Session, user_id: int) -> dict:
    try:
        from pyspark.sql import functions as F
    except ImportError:
        F = None

    notes = db.query(Note).filter(Note.user_id == user_id).all()
    records = _build_records(notes)

    if not records:
        return {
            **_empty_analytics(),
            "status": "ready",
            "engine": "local",
        }

    try:
        if F is None:
            raise RuntimeError("PySpark is not installed on this server.")

        spark = get_spark_session()
        df = spark.createDataFrame(records)

        subject_df = (
            df.groupBy("subject")
            .agg(F.count("*").alias("count"))
            .orderBy(F.desc("count"))
        )
        top_subjects = [
            {"subject": row["subject"], "count": row["count"]}
            for row in subject_df.collect()
        ]

        monthly_df = (
            df.groupBy("month_label", "year", "month")
            .agg(F.count("*").alias("count"))
            .orderBy("year", "month")
        )
        monthly_uploads = [
            {"month": row["month_label"], "count": row["count"]}
            for row in monthly_df.collect()
        ]

        type_df = (
            df.groupBy("file_type")
            .agg(F.count("*").alias("count"))
            .orderBy(F.desc("count"))
        )
        file_type_distribution = [
            {"type": row["file_type"], "count": row["count"]}
            for row in type_df.collect()
        ]

        return {
            "status": "ready",
            "engine": "local",
            "top_subjects": top_subjects,
            "monthly_uploads": monthly_uploads,
            "file_type_distribution": file_type_distribution,
            "total_files": len(records),
        }
    except Exception as exc:
        logger.exception("PySpark error: %s", exc)
        fallback = _python_fallback(records)
        fallback["engine"] = "python_fallback"
        fallback["status"] = "ready"
        return fallback


def compute_analytics_via_glue(db: Session, user_id: int) -> tuple[dict, int]:
    notes = db.query(Note).filter(Note.user_id == user_id).all()
    records = _build_records(notes)

    if not records:
        return {
            **_empty_analytics(),
            "status": "ready",
            "engine": "aws_glue",
        }, 200

    if not settings.AWS_GLUE_JOB_NAME:
        return {
            "status": "error",
            "engine": "aws_glue",
            "message": "AWS_GLUE_JOB_NAME is not configured.",
        }, 500

    bucket = settings.AWS_ANALYTICS_BUCKET_NAME or settings.AWS_BUCKET_NAME
    if not bucket:
        return {
            "status": "error",
            "engine": "aws_glue",
            "message": "AWS_ANALYTICS_BUCKET_NAME or AWS_BUCKET_NAME must be configured.",
        }, 500

    latest_job = (
        db.query(AnalyticsJob)
        .filter(AnalyticsJob.user_id == user_id)
        .order_by(AnalyticsJob.created_at.desc())
        .first()
    )

    if latest_job:
        maybe_ready = _resolve_existing_glue_job(db, bucket, latest_job)
        if maybe_ready:
            return maybe_ready, 200

    now = datetime.now(timezone.utc)
    if latest_job and latest_job.status == JOB_STATUS_SUCCESS:
        age = (now - latest_job.updated_at).total_seconds()
        if age <= settings.ANALYTICS_CACHE_SECONDS:
            cached = _read_result_from_s3(bucket, latest_job.output_s3_key)
            if cached:
                return cached, 200

    if latest_job and latest_job.status in JOB_STATUS_RUNNING:
        return {
            "status": "running",
            "engine": "aws_glue",
            "job_run_id": latest_job.job_run_id,
            "message": "Analytics job is still running on AWS Glue.",
        }, 202

    try:
        input_key, output_key = _upload_records_to_s3(bucket, user_id, records)
        job_run_id = _start_glue_job(bucket, input_key, output_key, user_id)
    except RuntimeError as exc:
        return {
            "status": "error",
            "engine": "aws_glue",
            "message": str(exc),
        }, 500

    analytics_job = AnalyticsJob(
        user_id=user_id,
        status="STARTING",
        job_run_id=job_run_id,
        input_s3_key=input_key,
        output_s3_key=output_key,
    )
    db.add(analytics_job)
    db.commit()

    return {
        "status": "running",
        "engine": "aws_glue",
        "job_run_id": job_run_id,
        "message": "Analytics job started on AWS Glue. Poll again shortly.",
    }, 202


def _resolve_existing_glue_job(
    db: Session,
    bucket: str,
    job: AnalyticsJob,
) -> dict | None:
    if not job.job_run_id:
        return None

    status, error_message = _get_glue_job_state(job.job_run_id)
    if status in JOB_STATUS_RUNNING:
        job.status = status
        db.commit()
        return None

    if status == JOB_STATUS_SUCCESS:
        result = _read_result_from_s3(bucket, job.output_s3_key)
        if result:
            job.status = JOB_STATUS_SUCCESS
            job.error_message = None
            db.commit()
            return result

    if status in JOB_STATUS_FAILURE:
        job.status = status
        job.error_message = error_message or "AWS Glue job failed."
        db.commit()
        return {
            "status": "error",
            "engine": "aws_glue",
            "message": job.error_message,
        }

    return None


def _build_records(notes: list[Note]) -> list[dict]:
    return [
        {
            "id": note.id,
            "title": note.title,
            "subject": note.subject,
            "file_type": note.file_type or "Unknown",
            "file_size": note.file_size or 0,
            "created_at": note.created_at.isoformat(),
            "year": note.created_at.year,
            "month": note.created_at.month,
            "month_label": note.created_at.strftime("%b %Y"),
        }
        for note in notes
    ]


def _empty_analytics() -> dict:
    return {
        "top_subjects": [],
        "monthly_uploads": [],
        "file_type_distribution": [],
        "total_files": 0,
    }


def _python_fallback(records: list[dict]) -> dict:
    subjects = Counter(record["subject"] for record in records)
    months = Counter(record["month_label"] for record in records)
    types = Counter(record["file_type"] for record in records)

    return {
        "top_subjects": [
            {"subject": key, "count": value}
            for key, value in subjects.most_common()
        ],
        "monthly_uploads": [
            {"month": key, "count": value}
            for key, value in sorted(months.items())
        ],
        "file_type_distribution": [
            {"type": key, "count": value}
            for key, value in types.most_common()
        ],
        "total_files": len(records),
    }


def _aws_session():
    session_kwargs = {"region_name": settings.AWS_REGION}
    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        session_kwargs.update(
            {
                "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
            }
        )
        if settings.AWS_SESSION_TOKEN:
            session_kwargs["aws_session_token"] = settings.AWS_SESSION_TOKEN
    return boto3.session.Session(**session_kwargs)


def _upload_records_to_s3(bucket: str, user_id: int, records: list[dict]) -> tuple[str, str]:
    timestamp = int(time.time())
    input_key = f"{settings.AWS_ANALYTICS_INPUT_PREFIX}/user_{user_id}/{timestamp}.json"
    output_key = f"{settings.AWS_ANALYTICS_OUTPUT_PREFIX}/user_{user_id}/latest.json"

    body = "\n".join(json.dumps(record) for record in records).encode("utf-8")
    try:
        _aws_session().client("s3").put_object(
            Bucket=bucket,
            Key=input_key,
            Body=body,
            ContentType="application/json",
        )
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed uploading analytics input to S3")
        raise RuntimeError("Failed to upload analytics input to S3.") from exc

    return input_key, output_key


def _start_glue_job(bucket: str, input_key: str, output_key: str, user_id: int) -> str:
    try:
        response = _aws_session().client("glue").start_job_run(
            JobName=settings.AWS_GLUE_JOB_NAME,
            Arguments={
                "--input_path": f"s3://{bucket}/{input_key}",
                "--output_path": f"s3://{bucket}/{output_key}",
                "--user_id": str(user_id),
            },
            Timeout=max(1, settings.AWS_GLUE_JOB_TIMEOUT_SECONDS // 60),
        )
        return response["JobRunId"]
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to start AWS Glue job")
        raise RuntimeError("Failed to start AWS Glue job.") from exc


def _get_glue_job_state(job_run_id: str) -> tuple[str, str | None]:
    try:
        response = _aws_session().client("glue").get_job_run(
            JobName=settings.AWS_GLUE_JOB_NAME,
            RunId=job_run_id,
            PredecessorsIncluded=False,
        )
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to fetch AWS Glue job status")
        return "ERROR", str(exc)

    job_run = response["JobRun"]
    return job_run["JobRunState"], job_run.get("ErrorMessage")


def _read_result_from_s3(bucket: str, output_key: str | None) -> dict | None:
    if not output_key:
        return None

    s3_client = _aws_session().client("s3")
    try:
        response = s3_client.get_object(Bucket=bucket, Key=output_key)
        payload = json.loads(response["Body"].read().decode("utf-8"))
    except s3_client.exceptions.NoSuchKey:
        return None
    except (BotoCoreError, ClientError, json.JSONDecodeError) as exc:
        logger.exception("Failed reading AWS Glue analytics result")
        return {
            "status": "error",
            "engine": "aws_glue",
            "message": f"Failed to read analytics result: {exc}",
        }

    payload["status"] = "ready"
    payload["engine"] = "aws_glue"
    return payload

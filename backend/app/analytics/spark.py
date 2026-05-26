"""
PySpark Analytics Engine
Uses real PySpark DataFrames to compute:
  1. Most uploaded subject
  2. Monthly upload counts
  3. File type distribution
"""
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from sqlalchemy.orm import Session
from ..notes.models import Note
import logging

logger = logging.getLogger(__name__)


def get_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("SmartNotesAnalytics")
        .master("local[*]")
        .config("spark.driver.memory", "512m")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )


def compute_analytics(db: Session, user_id: int) -> dict:
    """Load notes from SQLite into PySpark and compute analytics."""

    # ── Fetch data from DB ─────────────────────────────────
    notes = db.query(Note).filter(Note.user_id == user_id).all()

    if not notes:
        return {
            "top_subjects": [],
            "monthly_uploads": [],
            "file_type_distribution": [],
            "total_files": 0,
        }

    # ── Build raw records ──────────────────────────────────
    records = [
        {
            "id": n.id,
            "title": n.title,
            "subject": n.subject,
            "file_type": n.file_type or "Unknown",
            "file_size": n.file_size or 0,
            "created_at": n.created_at,
            "year": n.created_at.year,
            "month": n.created_at.month,
            "month_label": n.created_at.strftime("%b %Y"),
        }
        for n in notes
    ]

    spark = get_spark_session()

    try:
        df = spark.createDataFrame(records)

        # 1. Most uploaded subjects
        subject_df = (
            df.groupBy("subject")
            .agg(F.count("*").alias("count"))
            .orderBy(F.desc("count"))
        )
        top_subjects = [
            {"subject": row["subject"], "count": row["count"]}
            for row in subject_df.collect()
        ]

        # 2. Monthly upload count
        monthly_df = (
            df.groupBy("month_label", "year", "month")
            .agg(F.count("*").alias("count"))
            .orderBy("year", "month")
        )
        monthly_uploads = [
            {"month": row["month_label"], "count": row["count"]}
            for row in monthly_df.collect()
        ]

        # 3. File type distribution
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
            "top_subjects": top_subjects,
            "monthly_uploads": monthly_uploads,
            "file_type_distribution": file_type_distribution,
            "total_files": len(records),
        }

    except Exception as e:
        logger.error(f"PySpark error: {e}")
        # Fallback: pure-Python aggregation so the API never crashes
        return _python_fallback(records)
    finally:
        pass  # Keep SparkSession alive for reuse


def _python_fallback(records: list) -> dict:
    """Pure-Python fallback if Spark fails (e.g., no JVM in env)."""
    from collections import Counter

    subjects = Counter(r["subject"] for r in records)
    months = Counter(r["month_label"] for r in records)
    types = Counter(r["file_type"] for r in records)

    return {
        "top_subjects": [{"subject": k, "count": v} for k, v in subjects.most_common()],
        "monthly_uploads": [{"month": k, "count": v} for k, v in sorted(months.items())],
        "file_type_distribution": [{"type": k, "count": v} for k, v in types.most_common()],
        "total_files": len(records),
    }

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..database import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    subject = Column(String(100), nullable=False, index=True)
    description = Column(String(1000), nullable=True)
    file_key = Column(String(500), nullable=True)     # S3 object key
    file_url = Column(String(1000), nullable=True)    # Public or presigned URL
    file_name = Column(String(255), nullable=True)    # Original filename
    file_type = Column(String(50), nullable=True)     # pdf, docx, ppt, image
    file_size = Column(BigInteger, nullable=True)     # bytes
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="notes")

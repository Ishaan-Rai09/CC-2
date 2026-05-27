from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth.utils import get_current_user
from ..auth.models import User
from .spark import compute_analytics

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/")
def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns analytics computed via PySpark:
    - top_subjects
    - monthly_uploads
    - file_type_distribution
    - total_files
    """
    payload, status_code = compute_analytics(db, current_user.id)
    return JSONResponse(content=payload, status_code=status_code)

import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.authorization import require_permission
from app.db import get_db
from app.services.report import get_business_report

router = APIRouter(
    prefix="/api/v1/businesses/{business_id}/reports",
    tags=["Reports"],
)


@router.get("/summary")
def business_report_summary(
    business_id: uuid.UUID,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("reports:read")),
):
    if start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date must be on or before end_date",
        )

    return get_business_report(db, business_id, start_date, end_date)
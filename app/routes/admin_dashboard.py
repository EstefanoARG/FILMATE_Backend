import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.repositories import dashboard_repository
from app.schemas.dashboard import DashboardResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/dashboard", tags=["admin dashboard"])


@router.get("/", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)):
    return dashboard_repository.get_dashboard_data(db)

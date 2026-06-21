import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.repositories import dashboard_repository
from app.schemas.dashboard import DashboardResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/dashboard", tags=["admin dashboard"])


@router.get("/", response_model=DashboardResponse)
def get_dashboard(
    db: Annotated[Session, Depends(get_db)],
    periodo: Annotated[str, Query(regex="^(hoy|semana|mes|mes_anterior)$")] = "mes",
):
    return dashboard_repository.get_dashboard_data(db, periodo)

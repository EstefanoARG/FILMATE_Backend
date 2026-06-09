import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.repositories import transaction_repository
from app.schemas.transaction import TransactionListResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/reservations", tags=["admin reservations"])


@router.get("/", response_model=TransactionListResponse)
def list_all_reservations(
    estado: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return transaction_repository.list_transactions(db, estado=estado, page=page, limit=limit)

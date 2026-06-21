import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.repositories import transaction_repository
from app.schemas.transaction import TransactionListResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/reservations", tags=["admin reservations"])


@router.get("/", response_model=TransactionListResponse)
def list_all_reservations(
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    estado: Optional[str] = None,
):
    return transaction_repository.list_transactions(db, estado=estado, page=page, limit=limit)

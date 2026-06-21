import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.repositories import transaction_repository
from app.schemas.transaction import TransactionListResponse, TransactionDetail, ValidateQRSchema, ValidateResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/transactions", tags=["admin transactions"])


@router.get("/", response_model=TransactionListResponse)
def list_transactions(
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=500)] = 10,
    estado: Optional[str] = None,
    fecha: Optional[str] = None,
    buscar: Optional[str] = None,
    tipo: Optional[str] = None,
):
    return transaction_repository.list_transactions(db, tipo=tipo, estado=estado, fecha=fecha, buscar=buscar, page=page, limit=limit)


@router.get("/{transaction_id}", response_model=TransactionDetail, responses={404: {"description": "Transacción no encontrada"}})
def get_transaction_detail(transaction_id: int, db: Annotated[Session, Depends(get_db)]):
    result = transaction_repository.get_transaction_detail(db, transaction_id)
    if not result:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return result


@router.post("/validate", response_model=ValidateResponse)
def validate_ticket(payload: ValidateQRSchema, db: Annotated[Session, Depends(get_db)]):
    result = transaction_repository.validate_ticket_or_transaction(
        db, codigo_qr_token=payload.codigo_qr_token
    )
    return result

import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.transaccion import Transaccion
from app.schemas.transaccion import TransaccionResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.get("/user/{user_id}", response_model=List[TransaccionResponse])
def list_user_reservations(user_id: int, db: Annotated[Session, Depends(get_db)]):
    return db.query(Transaccion).filter(Transaccion.id_usuario == user_id).order_by(Transaccion.fecha_transaccion.desc()).all()


@router.get("/{transaction_id}", response_model=TransaccionResponse, responses={404: {"description": "Transacción no encontrada"}})
def get_reservation(transaction_id: int, db: Annotated[Session, Depends(get_db)]):
    txn = db.query(Transaccion).filter(Transaccion.id_transaccion == transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return txn

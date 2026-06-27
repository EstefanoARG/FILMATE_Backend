import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.repositories import ticket_repository, transaction_repository
from app.schemas.transaction import TransactionListResponse, TransactionDetail, ValidateQRSchema, ValidateResponse
from app.models.transaccion import Transaccion
from app.models.showtime import Funcion
from app.models.boleta_ticket import BoletaTicket
from app.models.detalle_boleta_asiento import DetalleBoletaAsiento
from app.models.seat import Asiento
from app.utils.ticket_pdf import build_ticket_pdf
from app.services.ticket_service import build_ticket_qr_payload

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


@router.get("/{transaction_id}/pdf")
def download_ticket_pdf_admin(transaction_id: int, db: Annotated[Session, Depends(get_db)]):
    ticket = ticket_repository.get_ticket_by_transaction_id(db, transaction_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    transaccion = db.query(Transaccion).filter(Transaccion.id_transaccion == transaction_id).first()
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    funcion = db.query(Funcion).filter(Funcion.id_funcion == transaccion.id_funcion).first()
    if not funcion:
        raise HTTPException(status_code=404, detail="Función no encontrada")
    tickets = db.query(BoletaTicket).filter(BoletaTicket.id_transaccion == transaction_id).all()
    detalle_asientos = db.query(DetalleBoletaAsiento).filter(DetalleBoletaAsiento.id_transaccion == transaction_id).all()
    seat_ids = [d.id_asiento for d in detalle_asientos]
    seats = db.query(Asiento).filter(Asiento.id_asiento.in_(seat_ids)).all()
    qr_payload = build_ticket_qr_payload(transaccion, funcion, seats, tickets)
    bundle = {"transaccion": transaccion, "funcion": funcion, "tickets": tickets, "seats": seats, "qr_payload": qr_payload}
    pdf_bytes = build_ticket_pdf(bundle)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=ticket_{transaction_id}.pdf"}
    )

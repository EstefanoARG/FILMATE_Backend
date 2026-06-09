import logging
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.order import CheckoutRequest, CheckoutResponse
from app.services.order_service import checkout_purchase
from app.services.ticket_service import build_ticket_qr_payload
from app.models.transaccion import Transaccion
from app.models.showtime import Funcion
from app.models.seat import Asiento
from app.models.boleta_ticket import BoletaTicket
from app.models.detalle_boleta_asiento import DetalleBoletaAsiento
from app.utils.ticket_pdf import build_ticket_pdf

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/client/tickets", tags=["client tickets"])

def _get_ticket_bundle(db: Session, transaction_id: int):
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
    return transaccion, funcion, tickets, seats

@router.post("/issue", response_model=CheckoutResponse)
def issue_ticket(payload: CheckoutRequest, db: Session = Depends(get_db)):
    logger.info("POST /client/tickets/issue - usuario=%s funcion=%s", payload.id_usuario, payload.id_funcion)
    try:
        return checkout_purchase(db, payload)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error en POST /client/tickets/issue: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/transaction/{transaction_id}")
def get_ticket_payload(transaction_id: int, db: Session = Depends(get_db)):
    logger.info("GET /client/tickets/transaction/%s", transaction_id)
    try:
        transaccion, funcion, tickets, seats = _get_ticket_bundle(db, transaction_id)
        qr_payload = build_ticket_qr_payload(transaccion, funcion, seats, tickets)
        return {
            "transaccion": {
                "id_transaccion": transaccion.id_transaccion,
                "monto_total": float(transaccion.monto_total),
                "estado_pago": transaccion.estado_pago,
            },
            "boletos": [{"id_ticket": t.id_ticket, "codigo_qr_token": t.codigo_qr_token, "estado_ticket": t.estado_ticket} for t in tickets],
            "qr": qr_payload,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/transaction/{transaction_id}/pdf")
def download_ticket_pdf(transaction_id: int, db: Session = Depends(get_db)):
    logger.info("GET /client/tickets/transaction/%s/pdf", transaction_id)
    try:
        transaccion, funcion, tickets, seats = _get_ticket_bundle(db, transaction_id)
        qr_payload = build_ticket_qr_payload(transaccion, funcion, seats, tickets)
        bundle = {"transaccion": transaccion, "funcion": funcion, "tickets": tickets, "seats": seats, "qr_payload": qr_payload}
        pdf_bytes = build_ticket_pdf(bundle)
        filename = f"ticket_transaccion_{transaction_id}.pdf"
        return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'})
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.order import CheckoutRequest, CheckoutResponse
from app.services.order_service import checkout_purchase

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/checkout", response_model=CheckoutResponse)
def checkout_order(payload: CheckoutRequest, db: Session = Depends(get_db)):
    logger.info("POST /orders/checkout - usuario=%s funcion=%s", payload.id_usuario, payload.id_funcion)
    try:
        return checkout_purchase(db, payload)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error en POST /orders/checkout: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))

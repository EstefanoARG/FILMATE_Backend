import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.order import CheckoutRequest, CheckoutResponse
from app.services.order_service import checkout_purchase

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/client/orders", tags=["client orders"])

@router.post("/checkout", response_model=CheckoutResponse, responses={500: {"description": "Internal server error"}})
def checkout_order(payload: CheckoutRequest, db: Annotated[Session, Depends(get_db)]):
    logger.info("POST /client/orders/checkout - usuario=%s funcion=%s", payload.id_usuario, payload.id_funcion)
    try:
        return checkout_purchase(db, payload)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error en POST /client/orders/checkout")
        raise HTTPException(status_code=500, detail=str(exc))
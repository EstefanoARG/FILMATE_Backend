import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.seat import SeatLockRequest, SeatLockResponse, SeatMapResponse
from app.services.seat_service import get_showtime_seat_map, lock_showtime_seats

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/seats", tags=["seats"])


@router.get("/showtime/{showtime_id}", response_model=SeatMapResponse, responses={500: {"description": "Internal server error"}})
def get_seat_map(showtime_id: int, db: Annotated[Session, Depends(get_db)]):
    logger.info("GET /seats/showtime/%s", showtime_id)
    try:
        return get_showtime_seat_map(db, showtime_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error en GET /seats/showtime/%s", showtime_id)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/lock", response_model=SeatLockResponse, responses={500: {"description": "Internal server error"}})
def lock_seats(payload: SeatLockRequest, db: Annotated[Session, Depends(get_db)]):
    logger.info("POST /seats/lock - funcion=%s asientos=%s", payload.id_funcion, payload.ids_asientos)
    try:
        result = lock_showtime_seats(db, payload.id_funcion, payload.ids_asientos)
        return SeatLockResponse(**result)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error en POST /seats/lock")
        raise HTTPException(status_code=500, detail=str(exc))

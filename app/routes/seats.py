import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.seat import SeatLockRequest, SeatLockResponse, SeatMapResponse
from app.services.seat_service import get_showtime_seat_map, lock_showtime_seats

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/seats", tags=["seats"])


@router.get("/showtime/{showtime_id}", response_model=SeatMapResponse)
def get_seat_map(showtime_id: int, db: Session = Depends(get_db)):
    logger.info("GET /seats/showtime/%s", showtime_id)
    try:
        return get_showtime_seat_map(db, showtime_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error en GET /seats/showtime/%s: %s", showtime_id, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/lock", response_model=SeatLockResponse)
def lock_seats(payload: SeatLockRequest, db: Session = Depends(get_db)):
    logger.info("POST /seats/lock - funcion=%s asientos=%s", payload.id_funcion, payload.ids_asientos)
    try:
        result = lock_showtime_seats(db, payload.id_funcion, payload.ids_asientos)
        return SeatLockResponse(**result)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error en POST /seats/lock: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))

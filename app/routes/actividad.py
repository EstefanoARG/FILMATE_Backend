import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.historial_actividad import HistorialActividad
from app.schemas.historial_actividad import HistorialActividadResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/actividad", tags=["actividad"])


@router.get("/feed", response_model=List[HistorialActividadResponse])
def get_feed(db: Session = Depends(get_db)):
    return db.query(HistorialActividad).order_by(HistorialActividad.fecha_evento.desc()).limit(50).all()


@router.get("/usuario/{user_id}", response_model=List[HistorialActividadResponse])
def get_user_activity(user_id: int, db: Session = Depends(get_db)):
    return (
        db.query(HistorialActividad)
        .filter(HistorialActividad.id_usuario == user_id)
        .order_by(HistorialActividad.fecha_evento.desc())
        .limit(50)
        .all()
    )

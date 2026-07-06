import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_superadmin
from app.models.log_actividad_sistema import LogActividadSistema
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/logs", tags=["admin logs"])


@router.get("/")
def list_logs(
    db: Annotated[Session, Depends(get_db)],
    _superadmin: Annotated[dict, Depends(get_current_superadmin)],
    modulo: Optional[str] = None,
    usuario_id: Optional[int] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    q: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
):
    query = db.query(LogActividadSistema)
    if modulo:
        query = query.filter(LogActividadSistema.modulo_afectado == modulo)
    if usuario_id:
        query = query.filter(LogActividadSistema.id_usuario == usuario_id)
    if fecha_desde:
        query = query.filter(LogActividadSistema.fecha_hora >= datetime.fromisoformat(fecha_desde))
    if fecha_hasta:
        query = query.filter(LogActividadSistema.fecha_hora <= datetime.fromisoformat(fecha_hasta))
    if q:
        query = query.filter(LogActividadSistema.accion_realizada.ilike(f"%{q}%"))
    total = query.count()
    items = query.order_by(LogActividadSistema.fecha_hora.desc()).offset((page - 1) * limit).limit(limit).all()
    return {"total": total, "page": page, "limit": limit, "items": items}

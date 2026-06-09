import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.permiso import Permiso
from app.models.rol_permiso import RolPermiso
from app.schemas.permiso import PermisoResponse
from app.schemas.rol import RolResponse
from app.models.role import Rol

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/roles", tags=["admin roles"])


@router.get("/", response_model=List[RolResponse])
def list_roles(db: Session = Depends(get_db)):
    return db.query(Rol).all()


@router.get("/{role_id}/permisos", response_model=List[PermisoResponse])
def get_role_permisos(role_id: int, db: Session = Depends(get_db)):
    permisos = (
        db.query(Permiso)
        .join(RolPermiso, RolPermiso.id_permiso == Permiso.id_permiso)
        .filter(RolPermiso.id_role == role_id)
        .all()
    )
    return permisos

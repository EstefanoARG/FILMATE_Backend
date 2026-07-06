import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_superadmin
from app.repositories import permission_repository
from app.schemas.permiso import PermisoCreate, PermisoResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/permisos", tags=["admin permisos"])


@router.get("/", response_model=List[PermisoResponse])
def list_permisos(
    db: Annotated[Session, Depends(get_db)],
    _superadmin: Annotated[dict, Depends(get_current_superadmin)],
):
    return permission_repository.list_permisos(db)


@router.post("/", response_model=PermisoResponse, status_code=201)
def create_permiso(
    payload: PermisoCreate,
    db: Annotated[Session, Depends(get_db)],
    _superadmin: Annotated[dict, Depends(get_current_superadmin)],
):
    try:
        return permission_repository.create_permiso(
            db, payload.codigo_permiso, payload.descripcion, payload.modulo
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/{permiso_id}")
def delete_permiso(
    permiso_id: int,
    db: Annotated[Session, Depends(get_db)],
    _superadmin: Annotated[dict, Depends(get_current_superadmin)],
):
    if not permission_repository.delete_permiso(db, permiso_id):
        raise HTTPException(status_code=404, detail="Permiso no encontrado")
    return {"message": "Permiso eliminado correctamente"}

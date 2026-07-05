from pydantic import BaseModel
from typing import List, Optional

from app.schemas.permiso import PermisoResponse


class RolResponse(BaseModel):
    id_role: int
    nombre_rol: str
    descripcion: Optional[str] = None

    model_config = {"from_attributes": True}


class RolCreate(BaseModel):
    nombre_rol: str
    descripcion: Optional[str] = None


class RolUpdate(BaseModel):
    nombre_rol: Optional[str] = None
    descripcion: Optional[str] = None


class RolWithPermisosResponse(BaseModel):
    id_role: int
    nombre_rol: str
    descripcion: Optional[str] = None
    permisos: List[PermisoResponse]

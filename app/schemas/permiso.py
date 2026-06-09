from pydantic import BaseModel
from typing import Optional


class PermisoResponse(BaseModel):
    id_permiso: int
    codigo_permiso: str
    descripcion: str
    modulo: str

    model_config = {"from_attributes": True}

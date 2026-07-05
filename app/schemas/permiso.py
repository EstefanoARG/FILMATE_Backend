from pydantic import BaseModel


class PermisoResponse(BaseModel):
    id_permiso: int
    codigo_permiso: str
    descripcion: str
    modulo: str

    model_config = {"from_attributes": True}


class PermisoCreate(BaseModel):
    codigo_permiso: str
    descripcion: str
    modulo: str

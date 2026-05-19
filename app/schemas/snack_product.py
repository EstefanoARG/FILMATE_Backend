from pydantic import BaseModel
from typing import Optional


class SnackProductBase(BaseModel):
    id_categoria: int
    nombre: str
    descripcion: Optional[str] = None
    precio_actual: float
    url_imagen: str


class SnackProductCreate(SnackProductBase):
    pass


class SnackProductResponse(SnackProductBase):
    id_producto: int
    is_activo: bool

    class Config:
        from_attributes = True
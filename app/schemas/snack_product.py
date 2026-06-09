from pydantic import BaseModel
from typing import Optional


class SnackProductBase(BaseModel):
    id_categoria_confi: int
    nombre_producto: str
    descripcion: Optional[str] = None
    precio: float
    url_imagen: str
    stock: int = 0


class SnackProductCreate(SnackProductBase):
    pass


class SnackProductResponse(SnackProductBase):
    id_producto: int

    model_config = {"from_attributes": True}

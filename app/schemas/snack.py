from typing import List, Optional

from pydantic import BaseModel


class SnackCategoryResponse(BaseModel):
    id_categoria_confi: int
    nombre_categoria: str

    model_config = {"from_attributes": True}


class SnackProductResponse(BaseModel):
    id_producto: int
    id_categoria_confi: int
    nombre_producto: str
    descripcion: Optional[str] = None
    precio: float
    url_imagen: str
    stock: int

    model_config = {"from_attributes": True}


class CartItem(BaseModel):
    id_producto: int
    cantidad: int


class CartCalculateRequest(BaseModel):
    items: List[CartItem]


class CartCalculateResponse(BaseModel):
    subtotal: float
    total: float

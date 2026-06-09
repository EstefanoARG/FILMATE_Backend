from pydantic import BaseModel
from typing import Optional


class DetalleBoletaConfiteriaCreate(BaseModel):
    id_transaccion: int
    id_producto: int
    cantidad: int
    precio_unitario: float


class DetalleBoletaConfiteriaResponse(BaseModel):
    id_detalle_confi: int
    id_transaccion: int
    id_producto: int
    cantidad: int
    precio_unitario: float

    model_config = {"from_attributes": True}

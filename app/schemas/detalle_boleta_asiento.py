from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DetalleBoletaAsientoCreate(BaseModel):
    id_transaccion: int
    id_asiento: int


class DetalleBoletaAsientoResponse(BaseModel):
    id_detalle_asiento: int
    id_transaccion: int
    id_asiento: int
    ingresado: bool
    fecha_ingreso: Optional[datetime] = None

    model_config = {"from_attributes": True}

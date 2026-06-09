from pydantic import BaseModel
from typing import Optional, List


class SeatCreate(BaseModel):
    fila: str
    columna: int
    tipo_asiento: str = "Regular"


class SeatResponse(BaseModel):
    id_asiento: int
    id_sala: int
    fila: str
    columna: int
    tipo_asiento: Optional[str] = "Regular"
    estado_asiento: str

    model_config = {"from_attributes": True}


class ShowtimeSeatItem(BaseModel):
    id_asiento: int
    fila: str
    columna: int
    tipo_asiento: Optional[str] = "Regular"
    estado: str


class SeatMapResponse(BaseModel):
    id_funcion: int
    id_sala: int
    asientos: List[ShowtimeSeatItem]


class SeatLockRequest(BaseModel):
    id_funcion: int
    ids_asientos: List[int]


class SeatLockResponse(BaseModel):
    id_funcion: int
    ids_asientos_bloqueados: List[int]
    estado: str

from pydantic import BaseModel
from typing import Optional


class RoomCreate(BaseModel):
    id_cine: int
    nombre_sala: str
    tipo_sala: str = "Stand."
    tipo_formato: str = "2D"
    capacidad_asientos: int = 0
    estado_sala: str = "Activa"


class RoomUpdate(BaseModel):
    nombre_sala: Optional[str] = None
    tipo_sala: Optional[str] = None
    tipo_formato: Optional[str] = None
    capacidad_asientos: Optional[int] = None
    estado_sala: Optional[str] = None


class RoomResponse(BaseModel):
    id_sala: int
    id_cine: int
    nombre_sala: str
    tipo_sala: str
    tipo_formato: str
    capacidad_asientos: int
    estado_sala: str

    model_config = {"from_attributes": True}

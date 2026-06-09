from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ShowtimeCreate(BaseModel):
    id_pelicula: int
    id_sala: int
    fecha_hora: datetime
    precio_base: float


class ShowtimeUpdate(BaseModel):
    fecha_hora: Optional[datetime] = None
    precio_base: Optional[float] = None


class ShowtimeResponse(BaseModel):
    id_funcion: int
    id_pelicula: int
    id_sala: int
    fecha_hora: datetime
    precio_base: float

    model_config = {"from_attributes": True}


class SeatAvailabilityItem(BaseModel):
    id_asiento: int
    fila: str
    columna: int
    estado: str


class ShowtimeAvailabilityItem(BaseModel):
    id_funcion: int
    id_pelicula: int
    titulo_pelicula: str
    id_sala: int
    nombre_sala: str
    fecha_hora: datetime
    precio_base: float
    asientos_totales: int
    asientos_disponibles: int


class CinemaShowtimesResponse(BaseModel):
    id_cine: int
    nombre_cine: str
    funciones: List[ShowtimeAvailabilityItem]

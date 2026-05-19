# backend/app/schemas/showtime_seat.py

from pydantic import BaseModel


class ShowtimeSeatBase(BaseModel):
    id_funcion: int
    id_asiento: int


class ShowtimeSeatCreate(ShowtimeSeatBase):
    pass


class ShowtimeSeatResponse(ShowtimeSeatBase):
    estado: str

    class Config:
        from_attributes = True
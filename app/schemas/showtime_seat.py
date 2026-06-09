from pydantic import BaseModel
from typing import Optional


class ShowtimeSeatCreate(BaseModel):
    id_funcion: int
    id_asiento: int
    estado: str = "Disponible"


class ShowtimeSeatResponse(BaseModel):
    id_funcion: int
    id_asiento: int
    estado: str

    model_config = {"from_attributes": True}

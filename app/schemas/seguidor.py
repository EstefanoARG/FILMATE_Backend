from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class SeguidorResponse(BaseModel):
    id_seguidor: int
    id_seguido: int
    fecha_seguimiento: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SeguirRequest(BaseModel):
    id_usuario: int
    id_seguir: int

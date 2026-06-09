from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class HistorialActividadResponse(BaseModel):
    id_actividad: int
    id_usuario: int
    tipo_evento: str
    id_referencia_usuario: Optional[int] = None
    id_referencia_pelicula: Optional[int] = None
    id_referencia_resena: Optional[int] = None
    texto_breve: Optional[str] = None
    fecha_evento: Optional[datetime] = None

    model_config = {"from_attributes": True}

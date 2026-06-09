from pydantic import BaseModel
from typing import Optional


class CinemaCreate(BaseModel):
    nombre_cine: str
    direccion: str
    horarios_apertura: Optional[str] = None
    url_mapa_embebido: Optional[str] = None
    estado_cine: str = "Activo"
    observaciones: Optional[str] = None


class CinemaResponse(BaseModel):
    id_cine: int
    nombre_cine: str
    direccion: str
    horarios_apertura: Optional[str] = None
    url_mapa_embebido: Optional[str] = None
    estado_cine: str
    observaciones: Optional[str] = None

    model_config = {"from_attributes": True}

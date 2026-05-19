from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MovieBase(BaseModel):
    titulo: str
    sinopsis: Optional[str] = None
    duracion_minutos: Optional[int] = None
    clasificacion_edad: Optional[str] = None
    url_poster: Optional[str] = None
    url_trailer: Optional[str] = None


class MovieCreate(MovieBase):
    pass


class MovieResponse(MovieBase):
    id_pelicula: int
    categoria_cartelera: str
    estado_registro: str
    fecha_creacion: datetime

    class Config:
        from_attributes = True
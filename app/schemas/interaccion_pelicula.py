from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class InteraccionPeliculaCreate(BaseModel):
    id_usuario: int
    id_pelicula: int
    vista: bool = False
    favorita: bool = False
    en_lista_seguimiento: bool = False


class InteraccionPeliculaResponse(BaseModel):
    id_usuario: int
    id_pelicula: int
    vista: bool
    favorita: bool
    en_lista_seguimiento: bool
    fecha_favorito: Optional[datetime] = None

    model_config = {"from_attributes": True}

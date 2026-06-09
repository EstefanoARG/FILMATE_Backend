from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ColeccionCreate(BaseModel):
    id_usuario: int
    titulo_coleccion: str
    descripcion: Optional[str] = None


class ColeccionResponse(BaseModel):
    id_coleccion: int
    id_usuario: int
    titulo_coleccion: str
    descripcion: Optional[str] = None
    fecha_creacion: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AgregarPeliculaColeccion(BaseModel):
    id_coleccion: int
    id_pelicula: int

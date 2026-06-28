from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MovieCreate(BaseModel):
    titulo: str
    anio_lanzamiento: int
    duracion_minutos: int
    clasificacion: str
    estado_pelicula: str = "PRÓXIMAMENTE"
    url_poster: str
    url_banner: Optional[str] = None
    url_trailer: Optional[str] = None
    sinopsis: Optional[str] = None
    elenco: Optional[str] = None
    director: str
    generos: List[int] = []
    tmdb_id: Optional[int] = None


class TMDBMovieCreate(BaseModel):
    estado_pelicula: str = "PRÓXIMAMENTE"
    url_trailer: Optional[str] = None
    clasificacion: Optional[str] = None


class MovieUpdate(BaseModel):
    titulo: Optional[str] = None
    anio_lanzamiento: Optional[int] = None
    duracion_minutos: Optional[int] = None
    clasificacion: Optional[str] = None
    estado_pelicula: Optional[str] = None
    url_poster: Optional[str] = None
    url_banner: Optional[str] = None
    url_trailer: Optional[str] = None
    sinopsis: Optional[str] = None
    elenco: Optional[str] = None
    director: Optional[str] = None


class GeneroSchema(BaseModel):
    id_genero: int
    nombre_genero: str

    model_config = {"from_attributes": True}


class MovieResponse(BaseModel):
    id_pelicula: int
    titulo: str
    anio_lanzamiento: int
    duracion_minutos: int
    clasificacion: str
    estado_pelicula: str
    url_poster: str
    url_banner: Optional[str] = None
    url_trailer: Optional[str] = None
    sinopsis: Optional[str] = None
    elenco: Optional[str] = None
    director: str
    total_vistas_comunidad: Optional[int] = 0
    total_favoritos_comunidad: Optional[int] = 0
    generos: List[GeneroSchema] = []
    tmdb_id: Optional[int] = None

    model_config = {"from_attributes": True}


class TMDBPreviewResponse(BaseModel):
    tmdb_id: int
    titulo: str
    sinopsis: Optional[str] = None
    duracion_minutos: Optional[int] = None
    anio_lanzamiento: Optional[int] = None
    director: str
    elenco: Optional[str] = None
    clasificacion: str
    url_poster: Optional[str] = None
    url_banner: Optional[str] = None
    url_trailer: Optional[str] = None
    tmdb_genres: List[dict] = []


class TMDBSearchItem(BaseModel):
    tmdb_id: int
    titulo: Optional[str] = None
    anio: Optional[int] = None
    sinopsis: Optional[str] = None
    url_poster: Optional[str] = None


class MovieDetailsResponse(BaseModel):
    id_pelicula: int
    titulo: str
    anio_lanzamiento: int
    duracion_minutos: int
    clasificacion: str
    estado_pelicula: str
    url_poster: str
    url_banner: Optional[str] = None
    url_trailer: Optional[str] = None
    sinopsis: Optional[str] = None
    elenco: Optional[str] = None
    director: str
    generos: Optional[List[str]] = None
    promedio_resenas: float = 0.0
    total_resenas: int = 0
    total_vistas_comunidad: Optional[int] = 0
    total_favoritos_comunidad: Optional[int] = 0

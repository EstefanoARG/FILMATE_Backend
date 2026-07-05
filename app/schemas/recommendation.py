"""Esquemas Pydantic para el Motor de Recomendación Inteligente (RF F-03 / HU-SOC-04)."""

from typing import List, Optional

from pydantic import BaseModel


class GeneroSimple(BaseModel):
    id_genero: int
    nombre_genero: str

    model_config = {"from_attributes": True}


class PeliculaRecomendada(BaseModel):
    """Payload mínimo que consume el carrusel de inicio del cliente."""

    id_pelicula: int
    titulo: str
    url_poster: str
    url_banner: Optional[str] = None
    director: str
    anio_lanzamiento: int
    clasificacion: Optional[str] = None
    duracion_minutos: Optional[int] = None
    estado_pelicula: Optional[str] = None
    promedio_resenas: float = 0.0
    total_resenas: int = 0
    total_favoritos_comunidad: int = 0
    generos: List[GeneroSimple] = []
    score: float = 0.0
    score_director: float = 0.0
    score_genero_top: float = 0.0
    score_genero_favorito: float = 0.0
    motivo: Optional[str] = None

    model_config = {"from_attributes": True}


class RecommendationSignals(BaseModel):
    """Señales internas que se usaron para puntuar (útil para depuración y tests)."""

    peliculas_favoritas_count: int = 0
    peliculas_vistas_count: int = 0
    resenas_5_estrellas_count: int = 0
    directores_clave_count: int = 0
    top_generos_count: int = 0
    compras_analizadas: int = 0


class RecommendationResponse(BaseModel):
    user_id: int
    total: int
    recomendaciones: List[PeliculaRecomendada]
    signals: Optional[RecommendationSignals] = None

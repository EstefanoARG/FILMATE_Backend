"""Capa de servicio del Motor de Recomendación Inteligente (RF F-03 / HU-SOC-04).

Combina las señales recogidas por `recommendation_repository` y construye el
payload final consumido por el carrusel de inicio del cliente.

Convenciones:
  * Se usa SQLAlchemy síncrono (consistente con el resto del backend). FastAPI
    ejecuta la coroutine en su threadpool, por lo que el endpoint no bloquea
    el event loop aunque la I/O sea bloqueante.
  * La función está envuelta en `try/except` y controla el ciclo de vida de
    la sesión de BD; en caso de fallo se hace rollback y se relanza.
"""

from __future__ import annotations

import asyncio
import logging
import math
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.repositories import recommendation_repository as repo
from app.schemas.recommendation import (
    GeneroSimple,
    PeliculaRecomendada,
    RecommendationResponse,
    RecommendationSignals,
)

logger = logging.getLogger(__name__)

# Pesos del algoritmo (ver recommendation_repository.get_ranked_candidates).
WEIGHT_DIRECTOR = 5.0
WEIGHT_TOP_GENRE = 2.0
WEIGHT_FAVORITE_GENRE = 1.0
MAX_TOP_GENRE_HITS = 4
MAX_FAVORITE_GENRE_HITS = 3


def _build_motivo(
    director_match: bool,
    top_hits: int,
    fav_hits: int,
    genres_names: List[str],
) -> Optional[str]:
    """Genera una explicación humana de por qué se recomienda la película."""
    parts: List[str] = []
    if director_match:
        parts.append("de un director que sigues")
    if top_hits > 0 and genres_names:
        muestra = ", ".join(genres_names[: min(2, len(genres_names))])
        parts.append(f"del género {muestra} que más consumes")
    elif fav_hits > 0 and genres_names:
        muestra = ", ".join(genres_names[: min(2, len(genres_names))])
        parts.append(f"similar a tus favoritas ({muestra})")
    return "Porque es " + " y ".join(parts) if parts else None


def _score_one(row: Dict[str, Any], genres: List[Dict[str, Any]]) -> PeliculaRecomendada:
    director_match = bool(row.get("has_director"))
    top_hits = int(row.get("top_genre_hits") or 0)
    fav_hits = int(row.get("fav_genre_hits") or 0)

    top_hits_capped = min(top_hits, MAX_TOP_GENRE_HITS)
    fav_hits_capped = min(fav_hits, MAX_FAVORITE_GENRE_HITS)

    score_director = WEIGHT_DIRECTOR if director_match else 0.0
    score_top = WEIGHT_TOP_GENRE * top_hits_capped
    score_fav = WEIGHT_FAVORITE_GENRE * fav_hits_capped
    community_bonus = math.log1p(int(row.get("total_favoritos_comunidad") or 0)) * 0.1
    total = round(score_director + score_top + score_fav + community_bonus, 2)

    generos_schema = [GeneroSimple(**g) for g in genres]
    nombres = [g["nombre_genero"] for g in genres]

    return PeliculaRecomendada(
        id_pelicula=int(row["id_pelicula"]),
        titulo=row["titulo"],
        url_poster=row["url_poster"],
        url_banner=row.get("url_banner"),
        director=row.get("director") or "",
        anio_lanzamiento=int(row.get("anio_lanzamiento") or 0),
        clasificacion=row.get("clasificacion"),
        duracion_minutos=int(row["duracion_minutos"]) if row.get("duracion_minutos") else None,
        estado_pelicula=row.get("estado_pelicula"),
        promedio_resenas=round(float(row.get("promedio_resenas") or 0.0), 1),
        total_resenas=int(row.get("total_resenas") or 0),
        total_favoritos_comunidad=int(row.get("total_favoritos_comunidad") or 0),
        generos=generos_schema,
        score=total,
        score_director=score_director,
        score_genero_top=score_top,
        score_genero_favorito=score_fav,
        motivo=_build_motivo(director_match, top_hits_capped, fav_hits_capped, nombres),
    )


# ---------------------------------------------------------------------------
# Lógica principal (síncrona — corre en el threadpool de FastAPI)
# ---------------------------------------------------------------------------

def _compute_recommendations_sync(
    user_id: int, limit: int = 10, db: Optional[Session] = None
) -> RecommendationResponse:
    own_session = db is None
    session = db or SessionLocal()
    try:
        favorites, watched = repo.get_excluded_movie_ids(session, user_id)
        excluded = list(favorites | watched)

        directors = repo.get_key_directors(session, user_id)
        top_genres = repo.get_top_genres_by_purchase(session, user_id)
        fav_genres = repo.get_favorite_genres(session, user_id)
        counters = repo.get_counters(session, user_id)

        ranked = repo.get_ranked_candidates(
            session,
            user_id=user_id,
            excluded_ids=excluded,
            directors=directors,
            top_genres=top_genres,
            favorite_genres=fav_genres,
            limit=limit,
        )

        if not ranked:
            session.commit()
            return RecommendationResponse(
                user_id=user_id,
                total=0,
                recomendaciones=[],
                signals=RecommendationSignals(
                    peliculas_favoritas_count=counters["favoritas"],
                    peliculas_vistas_count=counters["vistas"],
                    resenas_5_estrellas_count=counters["resenas_5"],
                    directores_clave_count=len(directors),
                    top_generos_count=len(top_genres),
                    compras_analizadas=counters["compras"],
                ),
            )

        genres_by_movie = repo.get_genres_for_movies(
            session, [int(r["id_pelicula"]) for r in ranked]
        )

        recomendaciones = [
            _score_one(row, genres_by_movie.get(int(row["id_pelicula"]), []))
            for row in ranked
        ]

        # Si el ranking dejó menos de `limit` candidatos (poco historial),
        # completamos con películas populares en cartelera.
        if len(recomendaciones) < limit:
            faltan = limit - len(recomendaciones)
            populares = session.execute(
                text(
                    """
                    SELECT id_pelicula, titulo, url_poster, url_banner, director,
                           anio_lanzamiento, clasificacion, duracion_minutos,
                           estado_pelicula, total_favoritos_comunidad
                    FROM peliculas
                    WHERE eliminado = 0
                      AND id_pelicula NOT IN :excl
                    ORDER BY total_favoritos_comunidad DESC, id_pelicula DESC
                    LIMIT :limit
                    """
                ),
                {"excl": tuple(excluded + [r.id_pelicula for r in recomendaciones]) or (0,),
                 "limit": faltan},
            ).all()
            pop_ids = [int(r[0]) for r in populares]
            pop_genres = repo.get_genres_for_movies(session, pop_ids)
            for r in populares:
                row = {
                    "id_pelicula": int(r[0]),
                    "titulo": r[1],
                    "url_poster": r[2],
                    "url_banner": r[3],
                    "director": r[4] or "",
                    "anio_lanzamiento": int(r[5] or 0),
                    "clasificacion": r[6],
                    "duracion_minutos": r[7],
                    "estado_pelicula": r[8],
                    "total_favoritos_comunidad": int(r[9] or 0),
                    "promedio_resenas": 0.0,
                    "total_resenas": 0,
                    "has_director": 0,
                    "top_genre_hits": 0,
                    "fav_genre_hits": 0,
                }
                recomendaciones.append(
                    _score_one(row, pop_genres.get(row["id_pelicula"], []))
                )

        session.commit()
        return RecommendationResponse(
            user_id=user_id,
            total=len(recomendaciones),
            recomendaciones=recomendaciones,
            signals=RecommendationSignals(
                peliculas_favoritas_count=counters["favoritas"],
                peliculas_vistas_count=counters["vistas"],
                resenas_5_estrellas_count=counters["resenas_5"],
                directores_clave_count=len(directors),
                top_generos_count=len(top_genres),
                compras_analizadas=counters["compras"],
            ),
        )
    except SQLAlchemyError as exc:
        if own_session:
            session.rollback()
        logger.exception("Error SQL al calcular recomendaciones para user_id=%s", user_id)
        raise exc
    except Exception as exc:
        if own_session:
            session.rollback()
        logger.exception("Error inesperado al calcular recomendaciones para user_id=%s", user_id)
        raise exc
    finally:
        if own_session:
            session.close()


# ---------------------------------------------------------------------------
# API pública (async para honrar la firma `getPersonalizedRecommendations`)
# ---------------------------------------------------------------------------

async def get_personalized_recommendations(
    user_id: int, limit: int = 10, db: Optional[Session] = None
) -> RecommendationResponse:
    """Punto de entrada asíncrono del motor de recomendación.

    Delega la consulta bloqueante a un thread del pool para no saturar el
    event loop de FastAPI.
    """
    if db is not None:
        return _compute_recommendations_sync(user_id, limit=limit, db=db)
    return await asyncio.to_thread(_compute_recommendations_sync, user_id, limit, None)

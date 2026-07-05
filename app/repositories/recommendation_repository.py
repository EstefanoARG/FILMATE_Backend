"""Capa de datos del Motor de Recomendación Inteligente (RF F-03 / HU-SOC-04).

Encapsula las consultas SQL que extraen las tres señales de preferencia del
usuario desde MySQL:

  A) Películas marcadas como favoritas (`interacciones_peliculas.favorita`).
  B) Directores de películas calificadas con 5 estrellas (`resenas`).
  C) Géneros más consumidos transaccionalmente
     (`transacciones` -> `funciones` -> `peliculas_generos`).

La consulta final agrega estas señales en una sola CTE que produce, por
película candidata, un score de relevancia y los componentes individuales
que lo originan, de modo que la capa de servicio solo tenga que formatear.
"""

from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session


# ---------------------------------------------------------------------------
# Señales individuales del usuario
# ---------------------------------------------------------------------------

def get_excluded_movie_ids(db: Session, user_id: int) -> Tuple[Set[int], Set[int]]:
    """Devuelve dos conjuntos: (favoritas, vistas) del usuario autenticado."""
    rows = db.execute(
        text(
            """
            SELECT id_pelicula, favorita, vista
            FROM interacciones_peliculas
            WHERE id_usuario = :user_id
              AND (favorita = 1 OR vista = 1)
            """
        ),
        {"user_id": user_id},
    ).all()
    favorites: Set[int] = set()
    watched: Set[int] = set()
    for pid, fav, seen in rows:
        if fav:
            favorites.add(int(pid))
        if seen:
            watched.add(int(pid))
    return favorites, watched


def get_key_directors(db: Session, user_id: int, limit: int = 5) -> List[str]:
    """Directores de películas que el usuario calificó con 5 estrellas."""
    rows = db.execute(
        text(
            """
            SELECT DISTINCT TRIM(p.director) AS director
            FROM resenas r
            INNER JOIN peliculas p ON p.id_pelicula = r.id_pelicula
            WHERE r.id_usuario = :user_id
              AND r.puntuacion_estrellas = 5
              AND p.eliminado = 0
              AND p.director IS NOT NULL
              AND TRIM(p.director) <> ''
            ORDER BY director ASC
            LIMIT :limit
            """
        ),
        {"user_id": user_id, "limit": limit},
    ).all()
    return [r[0] for r in rows if r[0]]


def get_top_genres_by_purchase(
    db: Session, user_id: int, limit: int = 3
) -> List[int]:
    """Géneros con mayor número de compras (transacciones) del usuario."""
    rows = db.execute(
        text(
            """
            SELECT pg.id_genero, COUNT(*) AS total
            FROM transacciones t
            INNER JOIN funciones f ON f.id_funcion = t.id_funcion
            INNER JOIN peliculas_generos pg ON pg.id_pelicula = f.id_pelicula
            WHERE t.id_usuario = :user_id
              AND t.estado_pago IN ('CONFIRMADO', 'APROBADO', 'PAGADO')
            GROUP BY pg.id_genero
            ORDER BY total DESC, pg.id_genero ASC
            LIMIT :limit
            """
        ),
        {"user_id": user_id, "limit": limit},
    ).all()
    return [int(r[0]) for r in rows if r[0] is not None]


def get_favorite_genres(db: Session, user_id: int) -> List[int]:
    """Géneros presentes en las películas favoritas del usuario."""
    rows = db.execute(
        text(
            """
            SELECT DISTINCT pg.id_genero
            FROM interacciones_peliculas ip
            INNER JOIN peliculas_generos pg ON pg.id_pelicula = ip.id_pelicula
            WHERE ip.id_usuario = :user_id
              AND ip.favorita = 1
            """
        ),
        {"user_id": user_id},
    ).all()
    return [int(r[0]) for r in rows if r[0] is not None]


def get_counters(db: Session, user_id: int) -> Dict[str, int]:
    """Conteos agregados útiles para la señal `signals` del payload."""
    row = db.execute(
        text(
            """
            SELECT
                (SELECT COUNT(*) FROM interacciones_peliculas
                 WHERE id_usuario = :user_id AND favorita = 1) AS favoritas,
                (SELECT COUNT(*) FROM interacciones_peliculas
                 WHERE id_usuario = :user_id AND vista = 1) AS vistas,
                (SELECT COUNT(*) FROM resenas
                 WHERE id_usuario = :user_id AND puntuacion_estrellas = 5) AS resenas_5,
                (SELECT COUNT(*) FROM transacciones
                 WHERE id_usuario = :user_id
                   AND estado_pago IN ('CONFIRMADO','APROBADO','PAGADO')) AS compras
            """
        ),
        {"user_id": user_id},
    ).first()
    if row is None:
        return {"favoritas": 0, "vistas": 0, "resenas_5": 0, "compras": 0}
    return {
        "favoritas": int(row[0] or 0),
        "vistas": int(row[1] or 0),
        "resenas_5": int(row[2] or 0),
        "compras": int(row[3] or 0),
    }


# ---------------------------------------------------------------------------
# Ranking de candidatas
# ---------------------------------------------------------------------------

def get_ranked_candidates(
    db: Session,
    user_id: int,
    excluded_ids: List[int],
    directors: List[str],
    top_genres: List[int],
    favorite_genres: List[int],
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Devuelve películas candidatas ordenadas por score de relevancia.

    El score se compone:
      + 5.0 si la candidata comparte director con los "directores clave".
      + 2.0 por cada género que coincida con los top géneros comprados (tope 4).
      + 1.0 por cada género que coincida con los géneros de las favoritas (tope 3).
      + bonus de comunidad: log(1 + total_favoritos_comunidad) * 0.1.

    Se excluyen: películas marcadas como favoritas o vistas por el usuario,
    películas con `eliminado = 1`, y películas sin géneros en común y sin
    director clave (evita devolver random).
    """
    if not directors and not top_genres and not favorite_genres:
        return []

    params: Dict[str, Any] = {
        "user_id": user_id,
        "limit": limit,
        "excluded": tuple(excluded_ids) if excluded_ids else (0,),
    }
    director_clause = ""
    if directors:
        director_clause = "OR p.director IN :directors"
        params["directors"] = tuple(directors)

    top_genre_clause = ""
    if top_genres:
        top_genre_clause = (
            "OR EXISTS (SELECT 1 FROM peliculas_generos pg2 "
            "WHERE pg2.id_pelicula = p.id_pelicula AND pg2.id_genero IN :top_genres)"
        )
        params["top_genres"] = tuple(top_genres)

    favorite_genre_clause = ""
    if favorite_genres:
        favorite_genre_clause = (
            "OR EXISTS (SELECT 1 FROM peliculas_generos pg3 "
            "WHERE pg3.id_pelicula = p.id_pelicula AND pg3.id_genero IN :fav_genres)"
        )
        params["fav_genres"] = tuple(favorite_genres)

    sql = text(
        f"""
        SELECT
            p.id_pelicula,
            p.titulo,
            p.url_poster,
            p.url_banner,
            p.director,
            p.anio_lanzamiento,
            p.clasificacion,
            p.duracion_minutos,
            p.estado_pelicula,
            p.total_favoritos_comunidad,
            COALESCE(stats.promedio, 0) AS promedio_resenas,
            COALESCE(stats.total_resenas, 0) AS total_resenas,
            CASE WHEN :has_directors = 1 AND p.director IN :directors_match
                 THEN 1 ELSE 0 END AS has_director,
            CASE WHEN :has_top = 1 THEN (
                SELECT COUNT(DISTINCT pg.id_genero)
                FROM peliculas_generos pg
                WHERE pg.id_pelicula = p.id_pelicula
                  AND pg.id_genero IN :top_match
            ) ELSE 0 END AS top_genre_hits,
            CASE WHEN :has_fav = 1 THEN (
                SELECT COUNT(DISTINCT pg.id_genero)
                FROM peliculas_generos pg
                WHERE pg.id_pelicula = p.id_pelicula
                  AND pg.id_genero IN :fav_match
            ) ELSE 0 END AS fav_genre_hits
        FROM peliculas p
        LEFT JOIN (
            SELECT id_pelicula,
                   AVG(puntuacion_estrellas) AS promedio,
                   COUNT(*) AS total_resenas
            FROM resenas
            GROUP BY id_pelicula
        ) stats ON stats.id_pelicula = p.id_pelicula
        WHERE p.eliminado = 0
          AND p.id_pelicula NOT IN :excluded
          AND (
              {director_clause}
              {top_genre_clause}
              {favorite_genre_clause}
          )
        ORDER BY has_director DESC,
                 top_genre_hits DESC,
                 fav_genre_hits DESC,
                 p.total_favoritos_comunidad DESC,
                 promedio_resenas DESC,
                 p.id_pelicula DESC
        LIMIT :limit
        """
    )

    # Inyectamos banderas y listas de match (necesarias para las CASE WHEN
    # de SQLAlchemy cuando las cláusulas anteriores están vacías).
    params["has_directors"] = 1 if directors else 0
    params["has_top"] = 1 if top_genres else 0
    params["has_fav"] = 1 if favorite_genres else 0
    params["directors_match"] = tuple(directors) if directors else ("",)
    params["top_match"] = tuple(top_genres) if top_genres else (0,)
    params["fav_match"] = tuple(favorite_genres) if favorite_genres else (0,)

    rows = db.execute(sql, params).all()
    return [dict(r._mapping) for r in rows]


def get_genres_for_movies(
    db: Session, movie_ids: List[int]
) -> Dict[int, List[Dict[str, Any]]]:
    """Devuelve un dict {id_pelicula: [{id_genero, nombre_genero}, ...]}."""
    if not movie_ids:
        return {}
    rows = db.execute(
        text(
            """
            SELECT pg.id_pelicula, g.id_genero, g.nombre_genero
            FROM peliculas_generos pg
            INNER JOIN generos g ON g.id_genero = pg.id_genero
            WHERE pg.id_pelicula IN :ids
            ORDER BY g.nombre_genero ASC
            """
        ),
        {"ids": tuple(movie_ids)},
    ).all()
    out: Dict[int, List[Dict[str, Any]]] = {mid: [] for mid in movie_ids}
    for pid, gid, name in rows:
        out.setdefault(int(pid), []).append(
            {"id_genero": int(gid), "nombre_genero": name}
        )
    return out

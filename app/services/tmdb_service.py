import os
from typing import Optional

import httpx

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_LANG = os.getenv("TMDB_LANG", "es-ES")
TMDB_BASE = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p"

_TIMEOUT = httpx.Timeout(15.0)


def _search_movie(query: str, page: int = 1) -> dict:
    with httpx.Client(timeout=_TIMEOUT) as client:
        resp = client.get(
            f"{TMDB_BASE}/search/movie",
            params={"api_key": TMDB_API_KEY, "query": query, "language": TMDB_LANG, "page": page},
        )
        resp.raise_for_status()
        return resp.json()


def _get_movie_detail(tmdb_id: int) -> dict:
    with httpx.Client(timeout=_TIMEOUT) as client:
        resp = client.get(
            f"{TMDB_BASE}/movie/{tmdb_id}",
            params={"api_key": TMDB_API_KEY, "language": TMDB_LANG},
        )
        resp.raise_for_status()
        return resp.json()


def _get_movie_credits(tmdb_id: int) -> dict:
    with httpx.Client(timeout=_TIMEOUT) as client:
        resp = client.get(
            f"{TMDB_BASE}/movie/{tmdb_id}/credits",
            params={"api_key": TMDB_API_KEY, "language": TMDB_LANG},
        )
        resp.raise_for_status()
        return resp.json()


def _get_movie_videos(tmdb_id: int) -> dict:
    with httpx.Client(timeout=_TIMEOUT) as client:
        resp = client.get(
            f"{TMDB_BASE}/movie/{tmdb_id}/videos",
            params={"api_key": TMDB_API_KEY, "language": "en-US"},
        )
        resp.raise_for_status()
        return resp.json()


def search_movie(query: str, page: int = 1) -> list[dict]:
    data = _search_movie(query, page)
    results = []
    for item in data.get("results", [])[:10]:
        results.append({
            "tmdb_id": item["id"],
            "titulo": item.get("title"),
            "anio": int(item["release_date"][:4]) if item.get("release_date") else None,
            "sinopsis": item.get("overview"),
            "url_poster": f"{IMAGE_BASE}/w500{item['poster_path']}" if item.get("poster_path") else None,
        })
    return results


def get_movie_preview(tmdb_id: int) -> dict:
    detail = _get_movie_detail(tmdb_id)
    credits = _get_movie_credits(tmdb_id)
    videos = _get_movie_videos(tmdb_id)

    director = "Desconocido"
    for crew in credits.get("crew", []):
        if crew.get("job") == "Director":
            director = crew["name"]
            break

    cast_list = [c["name"] for c in credits.get("cast", [])[:5]]
    elenco = ", ".join(cast_list) if cast_list else None

    trailer_url = None
    for video in videos.get("results", []):
        if video.get("type") == "Trailer" and video.get("site") == "YouTube":
            trailer_url = f"https://www.youtube.com/watch?v={video['key']}"
            break

    clasificacion = "18+" if detail.get("adult") else "PG-13"

    return {
        "tmdb_id": detail["id"],
        "titulo": detail.get("title"),
        "sinopsis": detail.get("overview"),
        "duracion_minutos": detail.get("runtime"),
        "anio_lanzamiento": int(detail["release_date"][:4]) if detail.get("release_date") else None,
        "director": director,
        "elenco": elenco,
        "clasificacion": clasificacion,
        "url_poster": f"{IMAGE_BASE}/w500{detail['poster_path']}" if detail.get("poster_path") else None,
        "url_banner": f"{IMAGE_BASE}/original{detail['backdrop_path']}" if detail.get("backdrop_path") else None,
        "url_trailer": trailer_url,
        "tmdb_genres": [{"id_tmdb": g["id"], "nombre": g["name"]} for g in detail.get("genres", [])],
    }


def map_tmdb_genres_to_local(tmdb_genres: list[dict], db_genres: list) -> list[int]:
    local_map = {g.nombre_genero.lower(): g.id_genero for g in db_genres}
    matched_ids = []
    for tg in tmdb_genres:
        name = tg.get("nombre", "").lower().strip()
        if name in local_map:
            matched_ids.append(local_map[name])
    return matched_ids

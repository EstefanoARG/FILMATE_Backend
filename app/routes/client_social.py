import logging
from typing import List, Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.dependencies import get_db
from app.models.historial_actividad import HistorialActividad
from app.schemas.historial_actividad import HistorialActividadResponse

# Importaciones necesarias para el summary
from app.models.user import Usuario
from app.models.review import Resena
from app.models.movie import Pelicula
from app.repositories.review_repository import get_trending_movies, get_suggested_users, record_profile_visit
from app.repositories.notification_repository import get_notifications, mark_notifications_read, mark_all_notifications_read

# Intentamos importar Seguidor (ajusta el nombre si en tu proyecto se llama distinto, ej. 'seguidores')
try:
    from app.models.seguidor import Seguidor
except ImportError:
    Seguidor = None

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/client/social", tags=["client social"])

TOP_FAVORITO_EVENT = "TOP_FAVORITO"

# Schema para recibir la bio
class ProfileUpdate(BaseModel):
    bio: str


def _enrich_activities(db: Session, eventos: List[HistorialActividad]) -> List[dict]:
    """Resuelve usernames/títulos para que el front pueda armar frases como
    'Kuki236 followed LuisBizagui69' sin tener que pedir cada nombre por separado."""
    actor_ids = {e.id_usuario for e in eventos}
    ref_user_ids = {e.id_referencia_usuario for e in eventos if e.id_referencia_usuario}
    ref_movie_ids = {e.id_referencia_pelicula for e in eventos if e.id_referencia_pelicula}

    all_user_ids = actor_ids | ref_user_ids
    usuarios_by_id = (
        {u.id_usuario: u for u in db.query(Usuario).filter(Usuario.id_usuario.in_(all_user_ids)).all()}
        if all_user_ids
        else {}
    )
    peliculas_by_id = (
        {p.id_pelicula: p for p in db.query(Pelicula).filter(Pelicula.id_pelicula.in_(ref_movie_ids)).all()}
        if ref_movie_ids
        else {}
    )

    resultado = []
    for evento in eventos:
        actor = usuarios_by_id.get(evento.id_usuario)
        referencia_usuario = usuarios_by_id.get(evento.id_referencia_usuario) if evento.id_referencia_usuario else None
        referencia_pelicula = peliculas_by_id.get(evento.id_referencia_pelicula) if evento.id_referencia_pelicula else None
        resultado.append(
            {
                "id_actividad": evento.id_actividad,
                "id_usuario": evento.id_usuario,
                "username": actor.username if actor else None,
                "url_perfil": actor.url_perfil if actor else None,
                "tipo_evento": evento.tipo_evento,
                "id_referencia_usuario": evento.id_referencia_usuario,
                "referencia_username": referencia_usuario.username if referencia_usuario else None,
                "id_referencia_pelicula": evento.id_referencia_pelicula,
                "referencia_pelicula_titulo": referencia_pelicula.titulo if referencia_pelicula else None,
                "id_referencia_resena": evento.id_referencia_resena,
                "texto_breve": evento.texto_breve,
                "fecha_evento": evento.fecha_evento,
            }
        )
    return resultado


@router.delete("/{activity_id}", responses={404: {"description": "Evento no encontrado"}})
def delete_activity(activity_id: int, db: Annotated[Session, Depends(get_db)]):
    evento = db.query(HistorialActividad).filter(HistorialActividad.id_actividad == activity_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    db.delete(evento)
    db.commit()
    return {"message": "Evento eliminado"}


@router.get("/feed")
def get_feed(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    limit: int = 20,
    offset: int = 0,
):
    """Feed combinado: reseñas de seguidos + actividad de seguidos + reseñas populares."""

    followed_ids = []
    if Seguidor:
        followed_ids = [
            row[0] for row in db.query(Seguidor.id_seguido).filter(Seguidor.id_seguidor == user_id).all()
        ]

    items = []

    if followed_ids:
        review_rows = (
            db.query(Resena, Usuario, Pelicula)
            .join(Usuario, Resena.id_usuario == Usuario.id_usuario)
            .join(Pelicula, Resena.id_pelicula == Pelicula.id_pelicula)
            .filter(Resena.id_usuario.in_(followed_ids))
            .order_by(Resena.fecha_publicacion.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        for resena, usuario, pelicula in review_rows:
            likes_count = (
                db.query(HistorialActividad)
                .filter(
                    HistorialActividad.tipo_evento == "LIKE_RESENA_RECIBIDO",
                    HistorialActividad.id_referencia_resena == resena.id_resena,
                )
                .count()
            )
            comments_count = (
                db.query(HistorialActividad)
                .filter(
                    HistorialActividad.tipo_evento == "COMENTARIO_RESENA",
                    HistorialActividad.id_referencia_resena == resena.id_resena,
                )
                .count()
            )
            liked_by_me = (
                db.query(HistorialActividad)
                .filter(
                    HistorialActividad.tipo_evento == "LIKE_RESENA_RECIBIDO",
                    HistorialActividad.id_referencia_resena == resena.id_resena,
                    HistorialActividad.id_referencia_usuario == user_id,
                )
                .first()
                is not None
            )
            items.append({
                "type": "review",
                "id": resena.id_resena,
                "id_usuario": resena.id_usuario,
                "username": usuario.username,
                "url_perfil": usuario.url_perfil,
                "puntuacion_estrellas": resena.puntuacion_estrellas,
                "comentario": resena.comentario,
                "fecha": resena.fecha_publicacion.isoformat() if resena.fecha_publicacion else None,
                "total_likes": likes_count,
                "total_comentarios": comments_count,
                "liked_by_me": liked_by_me,
                "pelicula": {
                    "id_pelicula": pelicula.id_pelicula,
                    "titulo": pelicula.titulo,
                    "url_poster": pelicula.url_poster,
                },
            })

        activity_rows = (
            db.query(HistorialActividad)
            .filter(
                HistorialActividad.id_usuario.in_(followed_ids),
                ~HistorialActividad.tipo_evento.in_([
                    'SEGUIDOR_RECIBIDO',
                    'LIKE_RESENA_RECIBIDO',
                    'COMENTARIO_RESENA',
                    'VISITA_PERFIL',
                ]),
            )
            .order_by(HistorialActividad.fecha_evento.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        activity_rich = _enrich_activities(db, activity_rows)
        for act in activity_rich:
            items.append({
                "type": "activity",
                "id_actividad": act["id_actividad"],
                "id_usuario": act["id_usuario"],
                "username": act["username"],
                "url_perfil": act["url_perfil"],
                "tipo_evento": act["tipo_evento"],
                "id_referencia_usuario": act["id_referencia_usuario"],
                "referencia_username": act["referencia_username"],
                "id_referencia_pelicula": act["id_referencia_pelicula"],
                "referencia_pelicula_titulo": act["referencia_pelicula_titulo"],
                "id_referencia_resena": act["id_referencia_resena"],
                "texto_breve": act["texto_breve"],
                "fecha": act["fecha_evento"].isoformat() if act["fecha_evento"] else None,
            })

    if not followed_ids or len(items) < limit:
        remaining = limit - len(items)
        popular_reviews = (
            db.query(Resena, Usuario, Pelicula)
            .join(Usuario, Resena.id_usuario == Usuario.id_usuario)
            .join(Pelicula, Resena.id_pelicula == Pelicula.id_pelicula)
            .order_by(Resena.fecha_publicacion.desc())
            .limit(remaining)
            .all()
        )
        for resena, usuario, pelicula in popular_reviews:
            if any(item.get("id") == resena.id_resena for item in items if item["type"] == "review"):
                continue
            likes_count = (
                db.query(HistorialActividad)
                .filter(
                    HistorialActividad.tipo_evento == "LIKE_RESENA_RECIBIDO",
                    HistorialActividad.id_referencia_resena == resena.id_resena,
                )
                .count()
            )
            comments_count = (
                db.query(HistorialActividad)
                .filter(
                    HistorialActividad.tipo_evento == "COMENTARIO_RESENA",
                    HistorialActividad.id_referencia_resena == resena.id_resena,
                )
                .count()
            )
            liked_by_me = (
                db.query(HistorialActividad)
                .filter(
                    HistorialActividad.tipo_evento == "LIKE_RESENA_RECIBIDO",
                    HistorialActividad.id_referencia_resena == resena.id_resena,
                    HistorialActividad.id_referencia_usuario == user_id,
                )
                .first()
                is not None
            )
            items.append({
                "type": "review",
                "id": resena.id_resena,
                "id_usuario": resena.id_usuario,
                "username": usuario.username,
                "url_perfil": usuario.url_perfil,
                "puntuacion_estrellas": resena.puntuacion_estrellas,
                "comentario": resena.comentario,
                "fecha": resena.fecha_publicacion.isoformat() if resena.fecha_publicacion else None,
                "total_likes": likes_count,
                "total_comentarios": comments_count,
                "liked_by_me": liked_by_me,
                "pelicula": {
                    "id_pelicula": pelicula.id_pelicula,
                    "titulo": pelicula.titulo,
                    "url_poster": pelicula.url_poster,
                },
            })

    items.sort(key=lambda x: x.get("fecha") or "", reverse=True)
    return items[offset:offset + limit]

@router.get("/activity/{user_id}", response_model=List[HistorialActividadResponse])
def get_user_activity(user_id: int, db: Annotated[Session, Depends(get_db)]):
    eventos = (
        db.query(HistorialActividad)
        .filter(HistorialActividad.id_usuario == user_id)
        .order_by(HistorialActividad.fecha_evento.desc())
        .limit(50)
        .all()
    )
    return _enrich_activities(db, eventos)


@router.get("/following-activity/{user_id}", response_model=List[HistorialActividadResponse])
def get_following_activity(user_id: int, db: Annotated[Session, Depends(get_db)]):
    """Feed de actividad solo de las cuentas que el usuario sigue (HU-SOC-11)."""
    if not Seguidor:
        return []

    seguido_ids = [
        row[0] for row in db.query(Seguidor.id_seguido).filter(Seguidor.id_seguidor == user_id).all()
    ]
    if not seguido_ids:
        return []

    eventos = (
        db.query(HistorialActividad)
        .filter(HistorialActividad.id_usuario.in_(seguido_ids))
        .order_by(HistorialActividad.fecha_evento.desc())
        .limit(50)
        .all()
    )
    return _enrich_activities(db, eventos)

@router.put("/profile/{user_id}", responses={404: {"description": "Usuario no encontrado"}})
def update_profile(user_id: int, payload: ProfileUpdate, db: Annotated[Session, Depends(get_db)]):
    """Actualiza la bio guardándola como un evento en el historial de actividad."""
    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    nueva_bio = HistorialActividad(
        id_usuario=user_id,
        tipo_evento='UPDATE_BIO',
        texto_breve=payload.bio
    )
    db.add(nueva_bio)
    db.commit()
    return {"message": "Perfil actualizado", "bio": payload.bio}

@router.get("/summary/{user_id}", responses={404: {"description": "Usuario no encontrado"}})
def get_social_summary(user_id: int, db: Annotated[Session, Depends(get_db)]):
    """Devuelve perfil (con la bio extraída), estadísticas y Top 5 ordenado."""
    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id, Usuario.eliminado == False).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    # Extraemos la bio desde el historial
    ultimo_evento_bio = (
        db.query(HistorialActividad)
        .filter(HistorialActividad.id_usuario == user_id, HistorialActividad.tipo_evento == 'UPDATE_BIO')
        .order_by(HistorialActividad.fecha_evento.desc())
        .first()
    )
    
    # Calculamos stats
    total_resenas = db.query(Resena).filter(Resena.id_usuario == user_id).count()
    seguidores_count = 0
    siguiendo_count = 0
    
    if Seguidor:
        seguidores_count = db.query(Seguidor).filter(Seguidor.id_seguido == user_id).count()
        siguiendo_count = db.query(Seguidor).filter(Seguidor.id_seguidor == user_id).count()
    
    # Top 5 destacadas: viven en historial_actividad (TOP_FAVORITO), separadas de la lista
    # completa de favoritas (InteraccionPelicula.favorita), en el orden en que se eligieron.
    top_movie_ids = [
        row[0]
        for row in db.query(HistorialActividad.id_referencia_pelicula)
        .filter(HistorialActividad.id_usuario == user_id, HistorialActividad.tipo_evento == TOP_FAVORITO_EVENT)
        .order_by(HistorialActividad.id_actividad.asc())
        .all()
    ]
    movies_by_id = {
        p.id_pelicula: p for p in db.query(Pelicula).filter(Pelicula.id_pelicula.in_(top_movie_ids)).all()
    } if top_movie_ids else {}
    top_movies = [movies_by_id[mid] for mid in top_movie_ids if mid in movies_by_id]
    
    return {
        "usuario": {
            "id": usuario.id_usuario,
            "username": usuario.username,
            "nombre": usuario.nombre,
            "bio": ultimo_evento_bio.texto_breve if ultimo_evento_bio else "",
            "url_perfil": usuario.url_perfil
        },
        "stats": {
            "total_reviews": total_resenas,
            "followers": seguidores_count,
            "following": siguiendo_count
        },
        "top_favorites": [
            {
                "id_pelicula": p.id_pelicula, 
                "titulo": p.titulo, 
                "url_poster": p.url_poster
            } for p in top_movies
        ]
    }


class VisitProfileRequest(BaseModel):
    visited_user_id: int


@router.get("/trending-movies")
def trending_movies(
    db: Annotated[Session, Depends(get_db)],
    limit: int = 5,
    user_id: Optional[int] = None,
):
    return get_trending_movies(db, limit, user_id)


@router.get("/suggested-users")
def suggested_users(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    limit: int = 5,
):
    return get_suggested_users(db, user_id, limit)


@router.post("/visit-profile")
def visit_profile(
    payload: VisitProfileRequest,
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    return record_profile_visit(db, user_id, payload.visited_user_id)


class MarkReadRequest(BaseModel):
    actividad_ids: List[int]


@router.get("/notifications")
def notifications(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    limit: int = 20,
):
    items, unread_count = get_notifications(db, user_id, limit)
    return {"notifications": items, "unread_count": unread_count}


@router.post("/notifications/read")
def notifications_read(
    payload: MarkReadRequest,
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    mark_notifications_read(db, user_id, payload.actividad_ids)
    return {"message": "Marcadas como leídas"}


@router.post("/notifications/read-all")
def notifications_read_all(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    mark_all_notifications_read(db, user_id)
    return {"message": "Todas marcadas como leídas"}
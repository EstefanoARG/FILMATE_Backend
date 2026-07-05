from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.review import Resena
from app.models.user import Usuario
from app.models.movie import Pelicula
from app.models.historial_actividad import HistorialActividad
from app.models.seguidor import Seguidor
from typing import List, Optional

LIKE_EVENT = "LIKE_RESENA_RECIBIDO"
COMMENT_EVENT = "COMENTARIO_RESENA"


def get_review(db: Session, review_id: int) -> Optional[Resena]:
    return db.query(Resena).filter(Resena.id_resena == review_id).first()


def count_review_likes(db: Session, review_id: int) -> int:
    return (
        db.query(HistorialActividad)
        .filter(HistorialActividad.tipo_evento == LIKE_EVENT, HistorialActividad.id_referencia_resena == review_id)
        .count()
    )


def count_review_comments(db: Session, review_id: int) -> int:
    return (
        db.query(HistorialActividad)
        .filter(HistorialActividad.tipo_evento == COMMENT_EVENT, HistorialActividad.id_referencia_resena == review_id)
        .count()
    )


def _comments_subquery(db: Session):
    return (
        db.query(
            HistorialActividad.id_referencia_resena.label("id_resena"),
            func.count(HistorialActividad.id_actividad).label("total_comentarios"),
        )
        .filter(HistorialActividad.tipo_evento == COMMENT_EVENT)
        .group_by(HistorialActividad.id_referencia_resena)
        .subquery()
    )


def list_reviews_for_movie(db: Session, movie_id: int, viewer_id: Optional[int] = None) -> List[dict]:
    likes_subq = (
        db.query(
            HistorialActividad.id_referencia_resena.label("id_resena"),
            func.count(HistorialActividad.id_actividad).label("total_likes"),
        )
        .filter(HistorialActividad.tipo_evento == LIKE_EVENT)
        .group_by(HistorialActividad.id_referencia_resena)
        .subquery()
    )
    comments_subq = _comments_subquery(db)

    rows = (
        db.query(Resena, Usuario, likes_subq.c.total_likes, comments_subq.c.total_comentarios)
        .join(Usuario, Resena.id_usuario == Usuario.id_usuario)
        .outerjoin(likes_subq, likes_subq.c.id_resena == Resena.id_resena)
        .outerjoin(comments_subq, comments_subq.c.id_resena == Resena.id_resena)
        .filter(Resena.id_pelicula == movie_id)
        .order_by(Resena.fecha_publicacion.desc())
        .all()
    )

    liked_dates = {}
    if viewer_id is not None:
        liked_dates = {
            row[0]: row[1]
            for row in db.query(HistorialActividad.id_referencia_resena, HistorialActividad.fecha_evento)
            .filter(HistorialActividad.tipo_evento == LIKE_EVENT, HistorialActividad.id_referencia_usuario == viewer_id)
            .all()
        }

    return [
        {
            "id_resena": resena.id_resena,
            "id_usuario": resena.id_usuario,
            "username": usuario.username,
            "url_perfil": usuario.url_perfil,
            "puntuacion_estrellas": resena.puntuacion_estrellas,
            "comentario": resena.comentario,
            "fecha_publicacion": resena.fecha_publicacion,
            "total_likes": total_likes or 0,
            "total_comentarios": total_comentarios or 0,
            "liked_by_me": resena.id_resena in liked_dates,
            "liked_at": liked_dates.get(resena.id_resena),
        }
        for resena, usuario, total_likes, total_comentarios in rows
    ]


def toggle_review_like(db: Session, review_id: int, user_id: int) -> Optional[dict]:
    review = get_review(db, review_id)
    if not review:
        return None

    existing = (
        db.query(HistorialActividad)
        .filter(
            HistorialActividad.tipo_evento == LIKE_EVENT,
            HistorialActividad.id_referencia_resena == review_id,
            HistorialActividad.id_referencia_usuario == user_id,
        )
        .first()
    )

    liked_at = None
    if existing:
        db.delete(existing)
        liked_by_me = False
    else:
        evento = HistorialActividad(
            id_usuario=review.id_usuario,
            tipo_evento=LIKE_EVENT,
            id_referencia_usuario=user_id,
            id_referencia_resena=review_id,
            texto_breve="Le gustó tu reseña",
        )
        db.add(evento)
        db.flush()
        db.refresh(evento)
        liked_at = evento.fecha_evento
        liked_by_me = True

    db.commit()

    return {
        "id_resena": review_id,
        "total_likes": count_review_likes(db, review_id),
        "liked_by_me": liked_by_me,
        "liked_at": liked_at,
    }


def create_review(db: Session, review: Resena) -> Resena:
    """Una sola reseña/calificación por usuario y película: si ya existe, se actualiza en vez
    de insertar otra fila (evita reseñas duplicadas que distorsionan el promedio)."""
    existing = (
        db.query(Resena)
        .filter(Resena.id_usuario == review.id_usuario, Resena.id_pelicula == review.id_pelicula)
        .first()
    )
    if existing:
        existing.puntuacion_estrellas = review.puntuacion_estrellas
        existing.comentario = review.comentario
        db.commit()
        db.refresh(existing)
        return existing

    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def update_review(db: Session, review_id: int, data: dict):
    review = get_review(db, review_id)
    if not review:
        return None
    for key, value in data.items():
        if hasattr(review, key) and value is not None:
            setattr(review, key, value)
    db.commit()
    db.refresh(review)
    return review


def list_reviews_by_user(db: Session, user_id: int) -> List[dict]:
    likes_subq = (
        db.query(
            HistorialActividad.id_referencia_resena.label("id_resena"),
            func.count(HistorialActividad.id_actividad).label("total_likes"),
        )
        .filter(HistorialActividad.tipo_evento == LIKE_EVENT)
        .group_by(HistorialActividad.id_referencia_resena)
        .subquery()
    )
    comments_subq = _comments_subquery(db)

    rows = (
        db.query(Resena, Pelicula, likes_subq.c.total_likes, comments_subq.c.total_comentarios)
        .join(Pelicula, Resena.id_pelicula == Pelicula.id_pelicula)
        .outerjoin(likes_subq, likes_subq.c.id_resena == Resena.id_resena)
        .outerjoin(comments_subq, comments_subq.c.id_resena == Resena.id_resena)
        .filter(Resena.id_usuario == user_id)
        .order_by(Resena.fecha_publicacion.desc())
        .all()
    )

    return [
        {
            "id_resena": resena.id_resena,
            "id_usuario": resena.id_usuario,
            "id_pelicula": resena.id_pelicula,
            "puntuacion_estrellas": resena.puntuacion_estrellas,
            "comentario": resena.comentario,
            "fecha_publicacion": resena.fecha_publicacion,
            "total_likes": total_likes or 0,
            "total_comentarios": total_comentarios or 0,
            "pelicula": {
                "id_pelicula": pelicula.id_pelicula,
                "titulo": pelicula.titulo,
                "url_poster": pelicula.url_poster,
                "anio_lanzamiento": pelicula.anio_lanzamiento,
            },
        }
        for resena, pelicula, total_likes, total_comentarios in rows
    ]


def list_reviews_by_following(db: Session, user_id: int) -> List[dict]:
    """Reseñas escritas por las cuentas que `user_id` sigue (HU-SOC-11)."""
    seguido_ids = [row[0] for row in db.query(Seguidor.id_seguido).filter(Seguidor.id_seguidor == user_id).all()]
    if not seguido_ids:
        return []

    likes_subq = (
        db.query(
            HistorialActividad.id_referencia_resena.label("id_resena"),
            func.count(HistorialActividad.id_actividad).label("total_likes"),
        )
        .filter(HistorialActividad.tipo_evento == LIKE_EVENT)
        .group_by(HistorialActividad.id_referencia_resena)
        .subquery()
    )
    comments_subq = _comments_subquery(db)

    rows = (
        db.query(Resena, Usuario, Pelicula, likes_subq.c.total_likes, comments_subq.c.total_comentarios)
        .join(Usuario, Resena.id_usuario == Usuario.id_usuario)
        .join(Pelicula, Resena.id_pelicula == Pelicula.id_pelicula)
        .outerjoin(likes_subq, likes_subq.c.id_resena == Resena.id_resena)
        .outerjoin(comments_subq, comments_subq.c.id_resena == Resena.id_resena)
        .filter(Resena.id_usuario.in_(seguido_ids))
        .order_by(Resena.fecha_publicacion.desc())
        .all()
    )

    liked_dates = {
        row[0]: row[1]
        for row in db.query(HistorialActividad.id_referencia_resena, HistorialActividad.fecha_evento)
        .filter(HistorialActividad.tipo_evento == LIKE_EVENT, HistorialActividad.id_referencia_usuario == user_id)
        .all()
    }

    return [
        {
            "id_resena": resena.id_resena,
            "id_usuario": resena.id_usuario,
            "username": usuario.username,
            "url_perfil": usuario.url_perfil,
            "puntuacion_estrellas": resena.puntuacion_estrellas,
            "comentario": resena.comentario,
            "fecha_publicacion": resena.fecha_publicacion,
            "total_likes": total_likes or 0,
            "total_comentarios": total_comentarios or 0,
            "liked_by_me": resena.id_resena in liked_dates,
            "liked_at": liked_dates.get(resena.id_resena),
            "pelicula": {
                "id_pelicula": pelicula.id_pelicula,
                "titulo": pelicula.titulo,
                "url_poster": pelicula.url_poster,
                "anio_lanzamiento": pelicula.anio_lanzamiento,
            },
        }
        for resena, usuario, pelicula, total_likes, total_comentarios in rows
    ]


def delete_review(db: Session, review_id: int) -> bool:
    review = get_review(db, review_id)
    if not review:
        return False
    db.delete(review)
    db.commit()
    return True


def get_review_detail(db: Session, review_id: int, viewer_id: Optional[int] = None) -> Optional[dict]:
    row = (
        db.query(Resena, Usuario, Pelicula)
        .join(Usuario, Resena.id_usuario == Usuario.id_usuario)
        .join(Pelicula, Resena.id_pelicula == Pelicula.id_pelicula)
        .filter(Resena.id_resena == review_id)
        .first()
    )
    if not row:
        return None

    resena, usuario, pelicula = row

    liked_by_me = False
    liked_at = None
    if viewer_id is not None:
        like_evento = (
            db.query(HistorialActividad)
            .filter(
                HistorialActividad.tipo_evento == LIKE_EVENT,
                HistorialActividad.id_referencia_resena == review_id,
                HistorialActividad.id_referencia_usuario == viewer_id,
            )
            .first()
        )
        if like_evento:
            liked_by_me = True
            liked_at = like_evento.fecha_evento

    return {
        "id_resena": resena.id_resena,
        "id_usuario": resena.id_usuario,
        "username": usuario.username,
        "url_perfil": usuario.url_perfil,
        "puntuacion_estrellas": resena.puntuacion_estrellas,
        "comentario": resena.comentario,
        "fecha_publicacion": resena.fecha_publicacion,
        "total_likes": count_review_likes(db, review_id),
        "liked_by_me": liked_by_me,
        "liked_at": liked_at,
        "total_comentarios": count_review_comments(db, review_id),
        "pelicula": {
            "id_pelicula": pelicula.id_pelicula,
            "titulo": pelicula.titulo,
            "url_poster": pelicula.url_poster,
            "anio_lanzamiento": pelicula.anio_lanzamiento,
        },
    }


def add_comment(db: Session, review_id: int, user_id: int, texto: str) -> Optional[dict]:
    review = get_review(db, review_id)
    if not review:
        return None

    evento = HistorialActividad(
        id_usuario=review.id_usuario,
        tipo_evento=COMMENT_EVENT,
        id_referencia_usuario=user_id,
        id_referencia_resena=review_id,
        texto_breve=texto,
    )
    db.add(evento)
    db.commit()
    db.refresh(evento)

    usuario = db.get(Usuario, user_id)
    return {
        "id_comentario": evento.id_actividad,
        "id_resena": review_id,
        "id_usuario": user_id,
        "username": usuario.username if usuario else "",
        "url_perfil": usuario.url_perfil if usuario else None,
        "texto": evento.texto_breve,
        "fecha_comentario": evento.fecha_evento,
    }


def list_comments(db: Session, review_id: int) -> List[dict]:
    rows = (
        db.query(HistorialActividad, Usuario)
        .join(Usuario, HistorialActividad.id_referencia_usuario == Usuario.id_usuario)
        .filter(
            HistorialActividad.tipo_evento == COMMENT_EVENT,
            HistorialActividad.id_referencia_resena == review_id,
        )
        .order_by(HistorialActividad.fecha_evento.asc())
        .all()
    )
    return [
        {
            "id_comentario": evento.id_actividad,
            "id_resena": review_id,
            "id_usuario": usuario.id_usuario,
            "username": usuario.username,
            "url_perfil": usuario.url_perfil,
            "texto": evento.texto_breve,
            "fecha_comentario": evento.fecha_evento,
        }
        for evento, usuario in rows
    ]


def delete_comment(db: Session, comment_id: int, user_id: int) -> bool:
    """Solo el autor del comentario puede borrarlo."""
    evento = (
        db.query(HistorialActividad)
        .filter(
            HistorialActividad.id_actividad == comment_id,
            HistorialActividad.tipo_evento == COMMENT_EVENT,
            HistorialActividad.id_referencia_usuario == user_id,
        )
        .first()
    )
    if not evento:
        return False
    db.delete(evento)
    db.commit()
    return True

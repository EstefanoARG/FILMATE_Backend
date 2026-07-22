from sqlalchemy import func, text, case
from sqlalchemy.orm import Session
from app.models.review import Resena
from app.models.user import Usuario
from app.models.movie import Pelicula
from app.models.historial_actividad import HistorialActividad
from app.models.seguidor import Seguidor
from app.models.interaccion_pelicula import InteraccionPelicula
from app.models.showtime import Funcion
from app.models.genre import Genero
from app.models.movie_genre import PeliculaGenero
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from app.repositories.movie_repository import attach_review_stats

LIKE_EVENT = "LIKE_RESENA_RECIBIDO"
COMMENT_EVENT = "COMENTARIO_RESENA"
VISITA_PERFIL_EVENT = "VISITA_PERFIL"


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


def get_trending_movies(db: Session, limit: int = 5, user_id: Optional[int] = None) -> List[dict]:
    seven_days_ago = func.now() - text("INTERVAL 7 DAY")

    signal_weights = {
        'VISTA': 1.0,
        'RESENA_PUBLICADA': 0.8,
        'COMPRA': 0.4,
    }

    excluded_movie_ids: set[int] = set()
    if user_id is not None:
        seen = (
            db.query(InteraccionPelicula.id_pelicula)
            .filter(
                InteraccionPelicula.id_usuario == user_id,
                InteraccionPelicula.vista == True,
            )
            .all()
        )
        excluded_movie_ids = {row[0] for row in seen}

    now = func.now()
    movies_with_functions = {
        row[0] for row in db.query(Funcion.id_pelicula)
        .filter(Funcion.fecha_hora >= now)
        .distinct()
        .all()
    }

    event_scores: dict[int, float] = {}

    for evento, weight in signal_weights.items():
        rows = (
            db.query(
                HistorialActividad.id_referencia_pelicula,
                HistorialActividad.fecha_evento,
            )
            .filter(
                HistorialActividad.tipo_evento == evento,
                HistorialActividad.fecha_evento >= seven_days_ago,
                HistorialActividad.id_referencia_pelicula.isnot(None),
            )
            .all()
        )

        for movie_id, fecha in rows:
            if movie_id in excluded_movie_ids:
                continue
            if fecha and fecha.tzinfo is None:
                fecha = fecha.replace(tzinfo=timezone.utc)
            delta = datetime.now(timezone.utc) - fecha if fecha else timedelta(days=7)
            delta_days = delta.days
            if delta_days <= 1:
                decay = 1.0
            elif delta_days <= 2:
                decay = 0.8
            elif delta_days <= 4:
                decay = 0.5
            else:
                decay = 0.2
            event_scores[movie_id] = event_scores.get(movie_id, 0) + weight * decay

    favoritos = (
        db.query(InteraccionPelicula.id_pelicula, func.count(InteraccionPelicula.id_usuario))
        .filter(
            InteraccionPelicula.favorita == True,
            ~InteraccionPelicula.id_pelicula.in_(list(excluded_movie_ids)) if excluded_movie_ids else True,
        )
        .group_by(InteraccionPelicula.id_pelicula)
        .all()
    )
    for movie_id, cnt in favoritos:
        event_scores[movie_id] = event_scores.get(movie_id, 0) + cnt * 0.5

    for movie_id in event_scores:
        if movie_id in movies_with_functions:
            event_scores[movie_id] += 0.5

    if not event_scores:
        popular = (
            db.query(Pelicula.id_pelicula)
            .filter(
                Pelicula.eliminado == False,
                ~Pelicula.id_pelicula.in_(list(excluded_movie_ids)) if excluded_movie_ids else True,
            )
            .order_by(Pelicula.total_vistas_comunidad.desc())
            .limit(limit)
            .all()
        )
        for (mid,) in popular:
            event_scores[mid] = 1

    ranked = sorted(event_scores.items(), key=lambda x: -x[1])[:limit]
    movie_ids = [mid for mid, _ in ranked]

    movies = (
        {m.id_pelicula: m for m in db.query(Pelicula).filter(Pelicula.id_pelicula.in_(movie_ids)).all()}
        if movie_ids else {}
    )

    result = []
    for movie_id, score in ranked:
        movie = movies.get(movie_id)
        if movie:
            result.append({
                "id_pelicula": movie.id_pelicula,
                "titulo": movie.titulo,
                "url_poster": movie.url_poster,
                "anio_lanzamiento": movie.anio_lanzamiento,
                "score": round(score, 1),
            })
    return result


def get_suggested_users(db: Session, user_id: int, limit: int = 5) -> List[dict]:
    followed_ids: set[int] = set()
    if Seguidor:
        followed_ids = {row[0] for row in db.query(Seguidor.id_seguido).filter(Seguidor.id_seguidor == user_id).all()}

    exclude_ids = followed_ids | {user_id}
    scores: dict[int, float] = {}

    mutual_counts: list = []
    similar: list = []
    visit_counts: list = []
    follower_set: set[int] = set()

    if Seguidor and followed_ids:
        mutual_rows = (
            db.query(Seguidor.id_seguido, func.count(Seguidor.id_seguidor).label('mutual'))
            .filter(
                Seguidor.id_seguidor.in_(list(followed_ids)),
                ~Seguidor.id_seguido.in_(list(exclude_ids)),
            )
            .group_by(Seguidor.id_seguido)
            .order_by(func.count(Seguidor.id_seguidor).desc())
            .all()
        )
        mutual_counts = [(uid, cnt) for uid, cnt in mutual_rows if uid is not None]
        for uid, cnt in mutual_counts:
            scores[uid] = scores.get(uid, 0) + cnt * 3

    user_movies = {
        r.id_pelicula for r in db.query(Resena.id_pelicula).filter(
            Resena.id_usuario == user_id,
            Resena.puntuacion_estrellas >= 4,
        ).all()
    }
    if user_movies:
        similar_rows = (
            db.query(Resena.id_usuario, func.count(Resena.id_resena).label('common'))
            .filter(
                Resena.id_pelicula.in_(list(user_movies)),
                Resena.puntuacion_estrellas >= 4,
                ~Resena.id_usuario.in_(list(exclude_ids)),
            )
            .group_by(Resena.id_usuario)
            .order_by(func.count(Resena.id_resena).desc())
            .all()
        )
        similar = [(uid, cnt) for uid, cnt in similar_rows if uid is not None]
        for uid, cnt in similar:
            scores[uid] = scores.get(uid, 0) + cnt * 2.5

    visit_rows = (
        db.query(
            HistorialActividad.id_referencia_usuario,
            func.count(HistorialActividad.id_actividad).label('visits'),
        )
        .filter(
            HistorialActividad.tipo_evento == VISITA_PERFIL_EVENT,
            HistorialActividad.id_usuario == user_id,
            HistorialActividad.id_referencia_usuario.isnot(None),
            ~HistorialActividad.id_referencia_usuario.in_(list(exclude_ids)),
        )
        .group_by(HistorialActividad.id_referencia_usuario)
        .all()
    )
    visit_counts = [(uid, cnt) for uid, cnt in visit_rows if uid is not None]
    for uid, cnt in visit_counts:
        scores[uid] = scores.get(uid, 0) + cnt * 4

    interaction_rows = (
        db.query(
            HistorialActividad.id_referencia_usuario,
            func.count(HistorialActividad.id_actividad).label('interactions'),
        )
        .filter(
            HistorialActividad.id_usuario == user_id,
            HistorialActividad.tipo_evento.in_([LIKE_EVENT, COMMENT_EVENT]),
            HistorialActividad.id_referencia_usuario.isnot(None),
            ~HistorialActividad.id_referencia_usuario.in_(list(exclude_ids)),
        )
        .group_by(HistorialActividad.id_referencia_usuario)
        .all()
    )
    for uid, cnt in interaction_rows:
        if uid is not None:
            scores[uid] = scores.get(uid, 0) + cnt * 2

    if Seguidor:
        follower_rows = (
            db.query(Seguidor.id_seguidor)
            .filter(
                Seguidor.id_seguido == user_id,
                ~Seguidor.id_seguidor.in_(list(exclude_ids)),
            )
            .all()
        )
        follower_set = {row[0] for row in follower_rows}
        for uid in follower_set:
            scores[uid] = scores.get(uid, 0) + 1.5

    if not scores:
        popular = (
            db.query(Usuario.id_usuario)
            .filter(~Usuario.id_usuario.in_(list(exclude_ids)))
            .limit(limit)
            .all()
        )
        for (uid,) in popular:
            scores[uid] = 1

    ranked = sorted(scores.items(), key=lambda x: -x[1])[:limit]
    suggested_ids = [uid for uid, _ in ranked]

    usuarios = {
        u.id_usuario: u
        for u in db.query(Usuario).filter(Usuario.id_usuario.in_(suggested_ids)).all()
    } if suggested_ids else {}

    result = []
    for uid, score in ranked:
        user = usuarios.get(uid)
        if not user:
            continue

        reason = None

        mc = next((cnt for u, cnt in mutual_counts if u == uid), 0)
        if mc >= 1:
            reason = f"{mc} amigo(s) en común"

        vc = next((cnt for u, cnt in visit_counts if u == uid), 0)
        if vc >= 1:
            reason = f"Visitaste su perfil ({vc} vez)" if vc == 1 else f"Visitaste su perfil ({vc} veces)"

        if not reason:
            sc = next((cnt for u, cnt in similar if u == uid), 0)
            if sc >= 1:
                reason = "Mismos gustos cinematográficos"

        if not reason and uid in follower_set:
            reason = "Te sigue"

        if not reason:
            reason = "Persona popular"

        result.append({
            "id_usuario": uid,
            "username": user.username,
            "url_perfil": user.url_perfil,
            "reason": reason,
        })

    return result


def record_profile_visit(db: Session, visitor_id: int, visited_id: int):
    if visitor_id == visited_id:
        return {"message": "Visit tracked"}

    evento = HistorialActividad(
        id_usuario=visited_id,
        tipo_evento=VISITA_PERFIL_EVENT,
        id_referencia_usuario=visitor_id,
    )
    db.add(evento)
    db.commit()
    return {"message": "Visit tracked"}


def get_personalized_recommendations(db: Session, user_id: Optional[int] = None, limit: int = 3) -> tuple[List[dict], list]:
    movies_in_theaters = {
        row[0] for row in db.query(Funcion.id_pelicula)
        .filter(Funcion.fecha_hora >= func.now())
        .distinct()
        .all()
    }

    if user_id is None:
        fallback = (
            db.query(Pelicula)
            .filter(
                Pelicula.id_pelicula.in_(list(movies_in_theaters)),
                Pelicula.eliminado == False,
            )
            .order_by(
                case(
                    (Pelicula.estado_pelicula == 'EN CARTELERA', 0),
                    else_=1,
                ),
                Pelicula.total_vistas_comunidad.desc(),
            )
            .limit(limit)
            .all()
        )
        movies = attach_review_stats(db, fallback)
        result = []
        for m in movies:
            genres_str = ', '.join(g.nombre_genero for g in m.generos if hasattr(g, 'nombre_genero'))
            result.append({
                "id_pelicula": m.id_pelicula,
                "titulo": m.titulo,
                "url_poster": m.url_poster,
                "anio_lanzamiento": m.anio_lanzamiento,
                "clasificacion": m.clasificacion,
                "duracion_minutos": m.duracion_minutos,
                "rating": getattr(m, 'promedio_resenas', 0),
                "total_resenas": getattr(m, 'total_resenas', 0),
                "total_vistas_comunidad": m.total_vistas_comunidad,
                "total_favoritos_comunidad": m.total_favoritos_comunidad,
                "estado_pelicula": m.estado_pelicula,
                "generos": genres_str,
            })
        return result, ["Lo más visto"]

    has_fav = db.query(InteraccionPelicula).filter(
        InteraccionPelicula.id_usuario == user_id,
        InteraccionPelicula.favorita == True,
    ).first()
    has_review = db.query(Resena).filter(
        Resena.id_usuario == user_id,
        Resena.puntuacion_estrellas >= 4,
    ).first()

    if not has_fav and not has_review:
        return get_personalized_recommendations(db, None, limit)

    excluded_ids: set[int] = set()
    watched = (
        db.query(InteraccionPelicula.id_pelicula)
        .filter(InteraccionPelicula.id_usuario == user_id, InteraccionPelicula.vista == True)
        .all()
    )
    excluded_ids |= {row[0] for row in watched}

    favorited = (
        db.query(InteraccionPelicula.id_pelicula)
        .filter(InteraccionPelicula.id_usuario == user_id, InteraccionPelicula.favorita == True)
        .all()
    )
    excluded_ids |= {row[0] for row in favorited}

    genre_freq: dict[int, float] = {}

    fav_genres = (
        db.query(PeliculaGenero.id_genero)
        .join(InteraccionPelicula, InteraccionPelicula.id_pelicula == PeliculaGenero.id_pelicula)
        .filter(
            InteraccionPelicula.id_usuario == user_id,
            InteraccionPelicula.favorita == True,
        )
        .all()
    )
    for (gid,) in fav_genres:
        genre_freq[gid] = genre_freq.get(gid, 0) + 3

    high_rated = (
        db.query(PeliculaGenero.id_genero)
        .join(Resena, Resena.id_pelicula == PeliculaGenero.id_pelicula)
        .filter(
            Resena.id_usuario == user_id,
            Resena.puntuacion_estrellas >= 4,
        )
        .all()
    )
    for (gid,) in high_rated:
        genre_freq[gid] = genre_freq.get(gid, 0) + 2.5

    recent_watched_ids = [
        row[0] for row in db.query(HistorialActividad.id_referencia_pelicula)
        .filter(
            HistorialActividad.id_usuario == user_id,
            HistorialActividad.tipo_evento == 'VISTA',
            HistorialActividad.id_referencia_pelicula.isnot(None),
        )
        .order_by(HistorialActividad.fecha_evento.desc())
        .limit(5)
        .all()
    ]
    if recent_watched_ids:
        watched_genres = (
            db.query(PeliculaGenero.id_genero)
            .filter(PeliculaGenero.id_pelicula.in_(recent_watched_ids))
            .all()
        )
        for (gid,) in watched_genres:
            genre_freq[gid] = genre_freq.get(gid, 0) + 2

    director_freq: dict[str, float] = {}
    actor_freq: dict[str, float] = {}

    fav_movies = (
        db.query(Pelicula.director, Pelicula.elenco)
        .join(InteraccionPelicula, InteraccionPelicula.id_pelicula == Pelicula.id_pelicula)
        .filter(
            InteraccionPelicula.id_usuario == user_id,
            InteraccionPelicula.favorita == True,
        )
        .all()
    )
    for dir_name, el_str in fav_movies:
        if dir_name:
            director_freq[dir_name] = director_freq.get(dir_name, 0) + 1
        if el_str:
            for actor in el_str.split(','):
                actor = actor.strip()
                if actor:
                    actor_freq[actor] = actor_freq.get(actor, 0) + 1

    high_rated_movies = (
        db.query(Pelicula.director, Pelicula.elenco)
        .join(Resena, Resena.id_pelicula == Pelicula.id_pelicula)
        .filter(
            Resena.id_usuario == user_id,
            Resena.puntuacion_estrellas >= 4,
        )
        .all()
    )
    for dir_name, el_str in high_rated_movies:
        if dir_name:
            director_freq[dir_name] = director_freq.get(dir_name, 0) + 1
        if el_str:
            for actor in el_str.split(','):
                actor = actor.strip()
                if actor:
                    actor_freq[actor] = actor_freq.get(actor, 0) + 1

    top_genre_ids = {gid for gid, _ in sorted(genre_freq.items(), key=lambda x: -x[1])[:5]}
    genre_name_map = {g.id_genero: g.nombre_genero for g in db.query(Genero).all()}
    top_genre_names = [genre_name_map.get(gid, '') for gid in top_genre_ids if genre_name_map.get(gid)]

    candidate_ids = {
        row[0] for row in db.query(PeliculaGenero.id_pelicula)
        .filter(PeliculaGenero.id_genero.in_(list(top_genre_ids)) if top_genre_ids else True)
        .all()
    } if top_genre_ids else set()

    candidate_ids -= excluded_ids
    candidate_ids &= movies_in_theaters

    if not candidate_ids:
        candidate_ids = movies_in_theaters - excluded_ids or {row[0] for row in db.query(Pelicula.id_pelicula).filter(Pelicula.eliminado == False).all()} - excluded_ids

    seven_days_ago = func.now() - text("INTERVAL 7 DAY")
    trending_counts = {}
    for evento, weight in [('VISTA', 1.0), ('RESENA_PUBLICADA', 0.8), ('COMPRA', 0.4)]:
        rows = (
            db.query(
                HistorialActividad.id_referencia_pelicula,
                func.count(HistorialActividad.id_actividad),
            )
            .filter(
                HistorialActividad.tipo_evento == evento,
                HistorialActividad.fecha_evento >= seven_days_ago,
                HistorialActividad.id_referencia_pelicula.in_(list(candidate_ids)),
            )
            .group_by(HistorialActividad.id_referencia_pelicula)
            .all()
        )
        for mid, cnt in rows:
            if mid is not None:
                trending_counts[mid] = trending_counts.get(mid, 0) + cnt * weight

    candidate_director_map = {}
    candidate_elenco_map = {}
    if candidate_ids:
        candidate_movies = db.query(Pelicula.id_pelicula, Pelicula.director, Pelicula.elenco).filter(
            Pelicula.id_pelicula.in_(list(candidate_ids))
        ).all()
        for mid, dir_name, el_str in candidate_movies:
            candidate_director_map[mid] = dir_name
            candidate_elenco_map[mid] = el_str

    scores: dict[int, float] = {}
    for mid in candidate_ids:
        score = 0.0

        mid_genres = {row[0] for row in db.query(PeliculaGenero.id_genero).filter(PeliculaGenero.id_pelicula == mid).all()}
        for gid in mid_genres:
            score += genre_freq.get(gid, 0)

        score += trending_counts.get(mid, 0) * 1.0

        score += 0.5

        director_name = candidate_director_map.get(mid)
        if director_name and director_name in director_freq:
            score += director_freq[director_name] * 6

        elenco_str = candidate_elenco_map.get(mid)
        if elenco_str:
            for actor_name in elenco_str.split(','):
                actor_name = actor_name.strip()
                if actor_name and actor_name in actor_freq:
                    score += actor_freq.get(actor_name, 0) * 2.5

        scores[mid] = score

    ranked = sorted(scores.items(), key=lambda x: -x[1])[:limit]
    movie_ids = [mid for mid, _ in ranked]

    movies = attach_review_stats(db, db.query(Pelicula).filter(Pelicula.id_pelicula.in_(movie_ids)).all())

    ordered = {m.id_pelicula: m for m in movies}
    result = []
    for mid in movie_ids:
        m = ordered.get(mid)
        if m:
            genres_str = ', '.join(g.nombre_genero for g in m.generos if hasattr(g, 'nombre_genero'))
            result.append({
                "id_pelicula": m.id_pelicula,
                "titulo": m.titulo,
                "url_poster": m.url_poster,
                "anio_lanzamiento": m.anio_lanzamiento,
                "clasificacion": m.clasificacion,
                "duracion_minutos": m.duracion_minutos,
                "rating": getattr(m, 'promedio_resenas', 0),
                "total_resenas": getattr(m, 'total_resenas', 0),
                "total_vistas_comunidad": m.total_vistas_comunidad,
                "total_favoritos_comunidad": m.total_favoritos_comunidad,
                "estado_pelicula": m.estado_pelicula,
                "generos": genres_str,
            })

    reason = f"Porque te gusta: {', '.join(top_genre_names[:3])}" if top_genre_names else "Basado en tu actividad"

    return result, top_genre_names[:3]

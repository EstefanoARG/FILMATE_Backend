from typing import List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.historial_actividad import HistorialActividad
from app.models.user import Usuario
from app.models.review import Resena
from app.models.movie import Pelicula
from app.models.notificacion_leida import NotificacionLeida

NOTIFICATION_EVENTS = [
    "SEGUIDOR_RECIBIDO",
    "LIKE_RESENA_RECIBIDO",
    "COMENTARIO_RESENA",
    "VISITA_PERFIL",
]


def _enrich_notification(db: Session, evento: HistorialActividad) -> dict:
    actor = db.query(Usuario).filter(Usuario.id_usuario == evento.id_referencia_usuario).first() if evento.id_referencia_usuario else None

    accion = ""
    if evento.tipo_evento == "SEGUIDOR_RECIBIDO":
        accion = "te siguió"
    elif evento.tipo_evento == "LIKE_RESENA_RECIBIDO":
        accion = "le gustó tu reseña"
    elif evento.tipo_evento == "COMENTARIO_RESENA":
        accion = "comentó tu reseña"
    elif evento.tipo_evento == "VISITA_PERFIL":
        accion = "visitó tu perfil"

    ref = {}
    if evento.id_referencia_pelicula:
        peli = db.query(Pelicula).filter(Pelicula.id_pelicula == evento.id_referencia_pelicula).first()
        if peli:
            ref["pelicula_titulo"] = peli.titulo
            ref["id_pelicula"] = peli.id_pelicula

    return {
        "id_actividad": evento.id_actividad,
        "tipo_evento": evento.tipo_evento,
        "actor_id": evento.id_referencia_usuario,
        "actor_username": actor.username if actor else None,
        "actor_avatar": actor.url_perfil if actor else None,
        "accion": accion,
        "texto_breve": evento.texto_breve,
        "fecha": evento.fecha_evento.isoformat() if evento.fecha_evento else None,
        "id_referencia_resena": evento.id_referencia_resena,
        **ref,
    }


def get_notifications(db: Session, user_id: int, limit: int = 20, offset: int = 0) -> tuple[List[dict], int]:
    read_ids = {
        row[0]
        for row in db.query(NotificacionLeida.id_actividad)
        .filter(NotificacionLeida.id_usuario == user_id)
        .all()
    }

    eventos = (
        db.query(HistorialActividad)
        .filter(
            HistorialActividad.id_usuario == user_id,
            HistorialActividad.tipo_evento.in_(NOTIFICATION_EVENTS),
            HistorialActividad.id_usuario != HistorialActividad.id_referencia_usuario,
        )
        .order_by(HistorialActividad.fecha_evento.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    unread_count = 0
    notifications = []
    for ev in eventos:
        is_read = ev.id_actividad in read_ids
        if not is_read:
            unread_count += 1
        enriched = _enrich_notification(db, ev)
        enriched["leida"] = is_read
        notifications.append(enriched)

    return notifications, unread_count


def mark_notifications_read(db: Session, user_id: int, actividad_ids: List[int]):
    for aid in actividad_ids:
        existing = (
            db.query(NotificacionLeida)
            .filter(
                NotificacionLeida.id_usuario == user_id,
                NotificacionLeida.id_actividad == aid,
            )
            .first()
        )
        if not existing:
            db.add(NotificacionLeida(id_usuario=user_id, id_actividad=aid))
    db.commit()


def mark_all_notifications_read(db: Session, user_id: int):
    unread = (
        db.query(HistorialActividad.id_actividad)
        .filter(
            HistorialActividad.id_usuario == user_id,
            HistorialActividad.tipo_evento.in_(NOTIFICATION_EVENTS),
            HistorialActividad.id_usuario != HistorialActividad.id_referencia_usuario,
        )
        .all()
    )

    read_ids = {
        row[0]
        for row in db.query(NotificacionLeida.id_actividad)
        .filter(NotificacionLeida.id_usuario == user_id)
        .all()
    }

    for (aid,) in unread:
        if aid not in read_ids:
            db.add(NotificacionLeida(id_usuario=user_id, id_actividad=aid))
    db.commit()

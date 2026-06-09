"""Servicios para consulta de funciones y horarios por sede."""

from datetime import date, datetime, time, timedelta

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.cinema import Cine
from app.models.movie import Pelicula
from app.models.room import Sala
from app.models.seat import Asiento
from app.models.showtime import Funcion
from app.models.showtime_seat import AsientoFuncion
from app.schemas.showtime import CinemaShowtimesResponse, ShowtimeAvailabilityItem


def list_showtimes_by_cinema(db: Session, cinema_id: int, only_future: bool = True) -> CinemaShowtimesResponse:
    cinema = db.query(Cine).filter(Cine.id_cine == cinema_id, Cine.eliminado == False).first()
    if not cinema:
        raise HTTPException(status_code=404, detail="Cine no encontrado")

    query = (
        db.query(Funcion, Pelicula, Sala)
        .join(Pelicula, Funcion.id_pelicula == Pelicula.id_pelicula)
        .join(Sala, Funcion.id_sala == Sala.id_sala)
        .filter(Sala.id_cine == cinema_id)
    )

    if only_future:
        query = query.filter(Funcion.fecha_hora >= datetime.now())

    rows = query.order_by(Funcion.fecha_hora).all()
    funciones = []

    for funcion, pelicula, sala in rows:
        asientos_totales = db.query(func.count(Asiento.id_asiento)).filter(
            Asiento.id_sala == sala.id_sala, Asiento.eliminado == False
        ).scalar() or 0

        asientos_ocupados = db.query(func.count(AsientoFuncion.id_asiento)).filter(
            AsientoFuncion.id_funcion == funcion.id_funcion,
            AsientoFuncion.estado.in_(["Ocupado", "Bloqueado"]),
        ).scalar() or 0

        funciones.append(
            ShowtimeAvailabilityItem(
                id_funcion=funcion.id_funcion,
                id_pelicula=pelicula.id_pelicula,
                titulo_pelicula=pelicula.titulo,
                id_sala=sala.id_sala,
                nombre_sala=sala.nombre_sala,
                fecha_hora=funcion.fecha_hora,
                precio_base=float(funcion.precio_base),
                asientos_totales=asientos_totales,
                asientos_disponibles=max(asientos_totales - asientos_ocupados, 0),
            )
        )

    return CinemaShowtimesResponse(
        id_cine=cinema.id_cine,
        nombre_cine=cinema.nombre_cine,
        funciones=funciones,
    )


def list_showtimes_by_movie(db: Session, movie_id: int):
    showtimes = (
        db.query(Funcion)
        .filter(Funcion.id_pelicula == movie_id)
        .all()
    )
    return showtimes


def list_showtimes_by_date(
    db: Session,
    target_date: date,
    cinema_id: int | None = None,
    movie_id: int | None = None,
):
    day_start = datetime.combine(target_date, time.min)
    day_end = day_start + timedelta(days=1)

    query = db.query(Funcion).filter(
        Funcion.fecha_hora >= day_start,
        Funcion.fecha_hora < day_end,
    )

    if movie_id is not None:
        query = query.filter(Funcion.id_pelicula == movie_id)

    if cinema_id is not None:
        query = query.join(Sala, Funcion.id_sala == Sala.id_sala).filter(Sala.id_cine == cinema_id)

    return query.order_by(Funcion.fecha_hora).all()

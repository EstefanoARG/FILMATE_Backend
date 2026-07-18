"""Servicios para consulta de funciones y horarios por sede."""

from datetime import date, datetime, time, timedelta

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.cinema import Cine
from app.models.movie import Pelicula
from app.models.room import Sala
from app.models.seat import Asiento
from app.models.showtime import Funcion
from app.models.showtime_seat import AsientoFuncion
from app.schemas.showtime import CinemaShowtimesResponse, ShowtimeAvailabilityItem


def _availability_rows_query(db: Session):
    seat_totals = (
        db.query(
            Asiento.id_sala.label("id_sala"),
            func.count(Asiento.id_asiento).label("asientos_totales"),
        )
        .filter(Asiento.eliminado == False)
        .group_by(Asiento.id_sala)
        .subquery()
    )
    occupied_totals = (
        db.query(
            AsientoFuncion.id_funcion.label("id_funcion"),
            func.count(AsientoFuncion.id_asiento).label("asientos_ocupados"),
        )
        .filter(AsientoFuncion.estado.in_(["Ocupado", "Bloqueado"]))
        .group_by(AsientoFuncion.id_funcion)
        .subquery()
    )

    return (
        db.query(
            Funcion.id_funcion.label("id_funcion"),
            Funcion.id_pelicula.label("id_pelicula"),
            Pelicula.titulo.label("titulo_pelicula"),
            Sala.id_sala.label("id_sala"),
            Sala.nombre_sala.label("nombre_sala"),
            Sala.tipo_sala.label("tipo_sala"),
            Sala.tipo_formato.label("tipo_formato"),
            Cine.id_cine.label("id_cine"),
            Cine.nombre_cine.label("nombre_cine"),
            Funcion.fecha_hora.label("fecha_hora"),
            Funcion.precio_base.label("precio_base"),
            func.coalesce(seat_totals.c.asientos_totales, 0).label("asientos_totales"),
            func.coalesce(occupied_totals.c.asientos_ocupados, 0).label("asientos_ocupados"),
        )
        .join(Pelicula, Funcion.id_pelicula == Pelicula.id_pelicula)
        .join(Sala, Funcion.id_sala == Sala.id_sala)
        .join(Cine, Sala.id_cine == Cine.id_cine)
        .outerjoin(seat_totals, seat_totals.c.id_sala == Sala.id_sala)
        .outerjoin(occupied_totals, occupied_totals.c.id_funcion == Funcion.id_funcion)
        .filter(
            Pelicula.eliminado == False,
            Sala.eliminado == False,
            Cine.eliminado == False,
        )
    )


def _row_to_availability_item(row) -> ShowtimeAvailabilityItem:
    asientos_totales = int(row.asientos_totales or 0)
    asientos_ocupados = int(row.asientos_ocupados or 0)

    return ShowtimeAvailabilityItem(
        id_funcion=row.id_funcion,
        id_pelicula=row.id_pelicula,
        titulo_pelicula=row.titulo_pelicula,
        id_sala=row.id_sala,
        nombre_sala=row.nombre_sala,
        tipo_sala=row.tipo_sala,
        tipo_formato=row.tipo_formato,
        id_cine=row.id_cine,
        nombre_cine=row.nombre_cine,
        fecha_hora=row.fecha_hora,
        precio_base=float(row.precio_base),
        asientos_totales=asientos_totales,
        asientos_disponibles=max(asientos_totales - asientos_ocupados, 0),
    )


def list_showtimes_by_cinema(db: Session, cinema_id: int, only_future: bool = True) -> CinemaShowtimesResponse:
    cinema = db.query(Cine).filter(Cine.id_cine == cinema_id, Cine.eliminado == False).first()
    if not cinema:
        raise HTTPException(status_code=404, detail="Cine no encontrado")

    query = _availability_rows_query(db).filter(Sala.id_cine == cinema_id)

    if only_future:
        query = query.filter(Funcion.fecha_hora >= datetime.now())

    rows = query.order_by(Funcion.fecha_hora).all()
    funciones = [_row_to_availability_item(row) for row in rows]

    return CinemaShowtimesResponse(
        id_cine=cinema.id_cine,
        nombre_cine=cinema.nombre_cine,
        funciones=funciones,
    )


def list_showtimes_by_movie(db: Session, movie_id: int) -> list[ShowtimeAvailabilityItem]:
    rows = (
        _availability_rows_query(db)
        .filter(Funcion.id_pelicula == movie_id)
        .order_by(Funcion.fecha_hora)
        .all()
    )
    return [_row_to_availability_item(row) for row in rows]


def list_showtimes_by_date(
    db: Session,
    target_date: date,
    cinema_id: int | None = None,
    movie_id: int | None = None,
) -> list[ShowtimeAvailabilityItem]:
    day_start = datetime.combine(target_date, time.min)
    day_end = day_start + timedelta(days=1)

    query = _availability_rows_query(db).filter(
        Funcion.fecha_hora >= day_start,
        Funcion.fecha_hora < day_end,
    )

    if movie_id is not None:
        query = query.filter(Funcion.id_pelicula == movie_id)

    if cinema_id is not None:
        query = query.filter(Sala.id_cine == cinema_id)

    rows = query.order_by(Funcion.fecha_hora).all()
    return [_row_to_availability_item(row) for row in rows]


def list_showtimes_by_range(
    db: Session,
    start_datetime: datetime,
    end_datetime: datetime,
    cinema_id: int | None = None,
    movie_id: int | None = None,
) -> list[ShowtimeAvailabilityItem]:
    query = _availability_rows_query(db).filter(
        Funcion.fecha_hora >= start_datetime,
        Funcion.fecha_hora <= end_datetime,
    )

    if movie_id is not None:
        query = query.filter(Funcion.id_pelicula == movie_id)

    if cinema_id is not None:
        query = query.filter(Sala.id_cine == cinema_id)

    rows = query.order_by(Funcion.fecha_hora).all()
    return [_row_to_availability_item(row) for row in rows]

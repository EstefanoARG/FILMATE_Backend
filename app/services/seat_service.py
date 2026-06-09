import asyncio
from typing import List

from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.seat import Asiento
from app.models.showtime import Funcion
from app.models.showtime_seat import AsientoFuncion
from app.schemas.seat import SeatMapResponse, ShowtimeSeatItem
from app.repositories.bloqueo_temporal_repository import bloquear_asientos
from app.websocket.seats_ws import publish_showtime_update


def get_showtime_seat_map(db: Session, showtime_id: int) -> SeatMapResponse:
    showtime = db.get(Funcion, showtime_id)
    if not showtime:
        raise HTTPException(status_code=404, detail="Función no encontrada")

    rows = (
        db.query(Asiento, AsientoFuncion.estado)
        .outerjoin(
            AsientoFuncion,
            and_(
                AsientoFuncion.id_asiento == Asiento.id_asiento,
                AsientoFuncion.id_funcion == showtime_id,
            ),
        )
        .filter(Asiento.id_sala == showtime.id_sala, Asiento.eliminado == False)
        .order_by(Asiento.fila, Asiento.columna)
        .all()
    )

    asientos = [
        ShowtimeSeatItem(
            id_asiento=seat.id_asiento,
            fila=seat.fila,
            columna=seat.columna,
            tipo_asiento=seat.tipo_asiento,
            estado=estado or "Disponible",
        )
        for seat, estado in rows
    ]

    return SeatMapResponse(
        id_funcion=showtime.id_funcion,
        id_sala=showtime.id_sala,
        asientos=asientos,
    )


def set_showtime_seats_state(db: Session, showtime_id: int, seat_ids: List[int], new_state: str) -> List[Asiento]:
    unique_ids = sorted(set(seat_ids))
    if not unique_ids:
        raise HTTPException(status_code=400, detail="Debe enviar al menos un asiento")

    showtime = db.get(Funcion, showtime_id)
    if not showtime:
        raise HTTPException(status_code=404, detail="Función no encontrada")

    seats = (
        db.query(Asiento)
        .filter(Asiento.id_sala == showtime.id_sala, Asiento.id_asiento.in_(unique_ids))
        .with_for_update()
        .all()
    )

    if len(seats) != len(unique_ids):
        raise HTTPException(status_code=404, detail="Uno o más asientos no pertenecen a la sala")

    existing_rows = (
        db.query(AsientoFuncion)
        .filter(
            AsientoFuncion.id_funcion == showtime_id,
            AsientoFuncion.id_asiento.in_(unique_ids),
        )
        .with_for_update()
        .all()
    )

    existing_by_id = {row.id_asiento: row for row in existing_rows}

    for seat_id in unique_ids:
        current = existing_by_id.get(seat_id)
        if current is None:
            db.add(AsientoFuncion(id_funcion=showtime_id, id_asiento=seat_id, estado=new_state))
            continue

        if current.estado == "Ocupado":
            raise HTTPException(status_code=409, detail=f"El asiento {seat_id} ya está ocupado")

        current.estado = new_state

    db.flush()
    return seats


def lock_showtime_seats(db: Session, showtime_id: int, seat_ids: List[int]) -> dict:
    with db.begin():
        bloquear_asientos(db, 0, showtime_id, seat_ids, minutos=10)

    publish_current_seat_map(db, showtime_id)
    return {"id_funcion": showtime_id, "ids_asientos_bloqueados": seat_ids, "estado": "Bloqueado"}


def publish_current_seat_map(db: Session, showtime_id: int) -> None:
    try:
        seat_map = get_showtime_seat_map(db, showtime_id)
        payload = {"type": "seat_map_update", "data": seat_map.model_dump()}
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(publish_showtime_update(showtime_id, payload))
        else:
            loop.create_task(publish_showtime_update(showtime_id, payload))
    except Exception:
        return

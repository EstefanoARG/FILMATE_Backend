"""Servicios de cierre de compra y creación de boletos."""

from datetime import datetime, timedelta
from typing import Dict, List
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.promotion import Promocion
from app.models.reservation import Reserva
from app.models.reservation_snack import ReservaSnack
from app.models.seat import Asiento
from app.models.showtime import Funcion
from app.models.snack_product import ProductoSnack
from app.models.tariff import Tarifa
from app.models.ticket import Boleto
from app.schemas.order import CheckoutRequest, CheckoutResponse
from app.schemas.ticket import TicketIssueResponse
from app.services.seat_service import publish_current_seat_map, set_showtime_seats_state
from app.services.ticket_service import build_ticket_qr_payload, build_ticket_response


def _get_tariff_price(db: Session, tariff_id: int) -> float:
    tarifa = db.get(Tarifa, tariff_id)
    if not tarifa:
        raise HTTPException(status_code=404, detail="Tarifa no encontrada")
    return float(tarifa.precio)


def _get_valid_promotion(db: Session, promotion_id: int | None) -> Promocion | None:
    if promotion_id is None:
        return None

    promocion = db.get(Promocion, promotion_id)
    if not promocion:
        raise HTTPException(status_code=404, detail="Promoción no encontrada")

    now = datetime.utcnow()
    if promocion.fecha_inicio and promocion.fecha_inicio > now:
        raise HTTPException(status_code=400, detail="La promoción aún no está vigente")
    if promocion.fecha_fin and promocion.fecha_fin < now:
        raise HTTPException(status_code=400, detail="La promoción ha expirado")

    return promocion


def checkout_purchase(db: Session, payload: CheckoutRequest) -> CheckoutResponse:
    """Cierra la compra, bloquea los asientos y genera los boletos."""

    if not payload.ids_asientos:
        raise HTTPException(status_code=400, detail="Debe seleccionar al menos un asiento")

    with db.begin():
        funcion = db.get(Funcion, payload.id_funcion)
        if not funcion:
            raise HTTPException(status_code=404, detail="Función no encontrada")

        tarifa_precio = _get_tariff_price(db, payload.id_tarifa)
        promocion = _get_valid_promotion(db, payload.id_promocion)

        seat_rows = db.execute(
            select(Asiento)
            .where(
                Asiento.id_sala == funcion.id_sala,
                Asiento.id_asiento.in_(sorted(set(payload.ids_asientos))),
            )
            .with_for_update()
        ).scalars().all()

        if len(seat_rows) != len(set(payload.ids_asientos)):
            raise HTTPException(status_code=404, detail="Uno o más asientos no pertenecen a la sala")

        set_showtime_seats_state(db, payload.id_funcion, payload.ids_asientos, "Vendido")

        subtotal_boletos = tarifa_precio * len(payload.ids_asientos)

        subtotal_snacks = 0.0
        snacks_data: List[Dict[str, float | int]] = []
        for snack_item in payload.snacks:
            producto = db.get(ProductoSnack, snack_item.id_producto)
            if not producto:
                raise HTTPException(status_code=404, detail=f"Snack no encontrado: {snack_item.id_producto}")

            precio_unitario = float(producto.precio_actual)
            subtotal_item = precio_unitario * snack_item.cantidad
            subtotal_snacks += subtotal_item
            snacks_data.append(
                {
                    "id_producto": producto.id_producto,
                    "cantidad": snack_item.cantidad,
                    "precio_unitario": precio_unitario,
                    "subtotal": subtotal_item,
                }
            )

        monto_subtotal = subtotal_boletos + subtotal_snacks

        descuento_aplicado = 0.0
        if promocion:
            if promocion.porcentaje_descuento:
                descuento_aplicado = monto_subtotal * (float(promocion.porcentaje_descuento) / 100.0)
            elif promocion.monto_descuento:
                descuento_aplicado = float(promocion.monto_descuento)

        monto_total = max(monto_subtotal - descuento_aplicado, 0.0)

        reserva = Reserva(
            id_usuario=payload.id_usuario,
            id_funcion=payload.id_funcion,
            id_promocion=payload.id_promocion,
            fecha_expiracion=payload.fecha_expiracion or (datetime.utcnow() + timedelta(minutes=15)),
            monto_subtotal=monto_subtotal,
            descuento_aplicado=descuento_aplicado,
            monto_total=monto_total,
            estado_pago="Pagado",
            metodo_pago=payload.metodo_pago,
            transaccion_id=payload.transaccion_id,
        )
        db.add(reserva)
        db.flush()

        boletos: List[Boleto] = []
        for seat in seat_rows:
            boleto = Boleto(
                id_reserva=reserva.id_reserva,
                id_funcion=payload.id_funcion,
                id_asiento=seat.id_asiento,
                id_tarifa=payload.id_tarifa,
                codigo_qr=uuid4().hex,
                precio_pagado=tarifa_precio,
                estado_ingreso="Vigente",
            )
            db.add(boleto)
            boletos.append(boleto)

        db.flush()

        for snack_row in snacks_data:
            db.add(
                ReservaSnack(
                    id_reserva=reserva.id_reserva,
                    id_producto=int(snack_row["id_producto"]),
                    cantidad=int(snack_row["cantidad"]),
                    precio_unitario=float(snack_row["precio_unitario"]),
                )
            )

        db.flush()

        qr_payload = build_ticket_qr_payload(reserva, funcion, seat_rows, boletos)

    publish_current_seat_map(db, payload.id_funcion)

    return CheckoutResponse(
        id_reserva=reserva.id_reserva,
        estado_pago=reserva.estado_pago,
        monto_subtotal=float(reserva.monto_subtotal),
        descuento_aplicado=float(reserva.descuento_aplicado),
        monto_total=float(reserva.monto_total),
        boletos=[build_ticket_response(ticket) for ticket in boletos],
        qr=qr_payload,
    )


def get_ticket_bundle_for_reservation(db: Session, reservation_id: int) -> TicketIssueResponse:
    """Recupera la reserva y reconstruye el payload QR de un ticket ya emitido."""

    reserva = db.get(Reserva, reservation_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    funcion = db.get(Funcion, reserva.id_funcion)
    if not funcion:
        raise HTTPException(status_code=404, detail="Función no encontrada para la reserva")

    boletos = db.execute(select(Boleto).where(Boleto.id_reserva == reservation_id)).scalars().all()
    seat_ids = [ticket.id_asiento for ticket in boletos]
    seat_rows = db.execute(select(Asiento).where(Asiento.id_asiento.in_(seat_ids))).scalars().all()

    snacks_query = (
        db.execute(
            select(ReservaSnack, ProductoSnack)
            .join(ProductoSnack, ProductoSnack.id_producto == ReservaSnack.id_producto)
            .where(ReservaSnack.id_reserva == reservation_id)
        ).all()
    )
    snacks = [
        {
            "producto": producto.nombre,
            "cantidad": rs.cantidad,
            "precio_unitario": float(rs.precio_unitario),
            "subtotal": float(rs.subtotal) if rs.subtotal is not None else float(rs.cantidad * rs.precio_unitario),
        }
        for rs, producto in snacks_query
    ]

    total_snacks = sum(s["subtotal"] for s in snacks)
    monto_total_real = float(reserva.monto_total)


    qr_payload = build_ticket_qr_payload(reserva, funcion, seat_rows, boletos)
    return TicketIssueResponse(
        reserva={
            "id_reserva": reserva.id_reserva,
            "id_usuario": reserva.id_usuario,
            "id_funcion": reserva.id_funcion,
            "id_promocion": reserva.id_promocion,
            "fecha_reserva": reserva.fecha_reserva,
            "fecha_expiracion": reserva.fecha_expiracion,
            "monto_subtotal": float(reserva.monto_subtotal),
            "descuento_aplicado": float(reserva.descuento_aplicado),
            "monto_total": monto_total_real,
            "estado_pago": reserva.estado_pago,
            "metodo_pago": reserva.metodo_pago,
            "transaccion_id": reserva.transaccion_id,
        },
        boletos=[build_ticket_response(ticket) for ticket in boletos],
        snacks=snacks, 
        qr=qr_payload,
    )

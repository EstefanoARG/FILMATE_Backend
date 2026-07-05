from typing import List
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transaccion import Transaccion
from app.models.detalle_boleta_asiento import DetalleBoletaAsiento
from app.models.detalle_boleta_confiteria import DetalleBoletaConfiteria
from app.models.boleta_ticket import BoletaTicket
from app.models.historial_actividad import HistorialActividad
from app.models.bloqueo_temporal import BloqueoTemporal
from app.models.seat import Asiento
from app.models.showtime import Funcion
from app.models.snack_product import ProductoConfiteria
from app.schemas.order import CheckoutRequest, CheckoutResponse
from app.services import payment_gateway_service
from app.services.seat_service import publish_current_seat_map, set_showtime_seats_state
from app.services.ticket_service import build_ticket_qr_payload


def checkout_purchase(db: Session, payload: CheckoutRequest) -> CheckoutResponse:
    if not payload.ids_asientos:
        raise HTTPException(status_code=400, detail="Debe seleccionar al menos un asiento")

    with db.begin():
        funcion = db.get(Funcion, payload.id_funcion)
        if not funcion:
            raise HTTPException(status_code=404, detail="Función no encontrada")

        seat_rows = (
            db.execute(
                select(Asiento)
                .where(
                    Asiento.id_sala == funcion.id_sala,
                    Asiento.id_asiento.in_(sorted(set(payload.ids_asientos))),
                )
                .with_for_update()
            )
            .scalars()
            .all()
        )

        if len(seat_rows) != len(set(payload.ids_asientos)):
            raise HTTPException(status_code=404, detail="Uno o más asientos no pertenecen a la sala")

        precio_base = float(funcion.precio_base)
        monto_boletos = precio_base * len(payload.ids_asientos)

        subtotal_snacks = 0.0
        detalle_confiteria = []
        for snack_item in payload.snacks:
            producto = db.get(ProductoConfiteria, snack_item.id_producto)
            if not producto:
                raise HTTPException(status_code=404, detail=f"Snack no encontrado: {snack_item.id_producto}")

            precio_unitario = float(producto.precio)
            subtotal_item = precio_unitario * snack_item.cantidad
            subtotal_snacks += subtotal_item
            detalle_confiteria.append(
                DetalleBoletaConfiteria(
                    id_producto=producto.id_producto,
                    cantidad=snack_item.cantidad,
                    precio_unitario=precio_unitario,
                )
            )

        monto_total = monto_boletos + subtotal_snacks

        # Se cobra ANTES de tocar el estado de los asientos: si la pasarela rechaza, no debe
        # quedar ningún asiento marcado como ocupado ni transacción creada.
        resultado_pago = payment_gateway_service.cobrar(payload.token_pago, monto_total, payload.email)
        if not resultado_pago["aprobado"]:
            raise HTTPException(status_code=402, detail=resultado_pago["mensaje"])

        set_showtime_seats_state(db, payload.id_funcion, payload.ids_asientos, "Ocupado")

        db.query(BloqueoTemporal).filter(
            BloqueoTemporal.id_funcion == payload.id_funcion,
            BloqueoTemporal.id_asiento.in_(sorted(set(payload.ids_asientos))),
        ).delete(synchronize_session=False)

        transaccion = Transaccion(
            id_usuario=payload.id_usuario,
            id_funcion=payload.id_funcion,
            monto_boletos=monto_boletos,
            monto_confiteria=subtotal_snacks,
            monto_total=monto_total,
            estado_pago="Aprobado",
            metodo_pago=payload.metodo_pago or resultado_pago["metodo_pago"],
        )
        db.add(transaccion)
        db.flush()

        tickets: List[BoletaTicket] = []
        detalle_asientos: List[DetalleBoletaAsiento] = []
        for seat in seat_rows:
            dba = DetalleBoletaAsiento(
                id_transaccion=transaccion.id_transaccion,
                id_asiento=seat.id_asiento,
                ingresado=False,
            )
            db.add(dba)
            detalle_asientos.append(dba)

            ticket = BoletaTicket(
                id_transaccion=transaccion.id_transaccion,
                codigo_qr_token=uuid4().hex,
                estado_ticket="Valido",
            )
            db.add(ticket)
            tickets.append(ticket)

        for dc in detalle_confiteria:
            dc.id_transaccion = transaccion.id_transaccion
            db.add(dc)

        db.flush()

        pelicula = funcion.pelicula
        evento = HistorialActividad(
            id_usuario=payload.id_usuario,
            tipo_evento="COMPRA",
            id_referencia_pelicula=funcion.id_pelicula,
            texto_breve=f"Compró {len(payload.ids_asientos)} boleto(s) para {pelicula.titulo if pelicula else ''}",
        )
        db.add(evento)

        qr_payload = build_ticket_qr_payload(transaccion, funcion, seat_rows, tickets)

    publish_current_seat_map(db, payload.id_funcion)

    boletos_data = [
        {
            "id_ticket": t.id_ticket,
            "id_asiento": d.id_asiento,
            "codigo_qr_token": t.codigo_qr_token,
            "estado_ticket": t.estado_ticket,
        }
        for t, d in zip(tickets, detalle_asientos)
    ]

    return CheckoutResponse(
        id_transaccion=transaccion.id_transaccion,
        estado_pago=transaccion.estado_pago,
        monto_boletos=float(transaccion.monto_boletos),
        monto_confiteria=float(transaccion.monto_confiteria),
        monto_total=float(transaccion.monto_total),
        boletos=boletos_data,
        qr=qr_payload,
        id_cargo_pasarela=resultado_pago["id_cargo"],
    )

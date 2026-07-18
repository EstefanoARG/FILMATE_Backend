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
    ids_asientos = sorted(set(payload.ids_asientos or []))
    has_seats = bool(ids_asientos)
    has_snacks = bool(payload.snacks)

    if not has_seats and not has_snacks:
        raise HTTPException(status_code=400, detail="Debe seleccionar al menos un asiento o producto de dulceria")

    if has_seats and not payload.id_funcion:
        raise HTTPException(status_code=400, detail="Debe seleccionar una funcion para reservar asientos")

    with db.begin():
        funcion = None
        seat_rows: List[Asiento] = []
        monto_boletos = 0.0

        if has_seats:
            funcion = db.get(Funcion, payload.id_funcion)
            if not funcion:
                raise HTTPException(status_code=404, detail="Funcion no encontrada")

            seat_rows = (
                db.execute(
                    select(Asiento)
                    .where(
                        Asiento.id_sala == funcion.id_sala,
                        Asiento.id_asiento.in_(ids_asientos),
                    )
                    .with_for_update()
                )
                .scalars()
                .all()
            )

            if len(seat_rows) != len(ids_asientos):
                raise HTTPException(status_code=404, detail="Uno o mas asientos no pertenecen a la sala")

            precio_base = float(funcion.precio_base)
            monto_boletos = precio_base * len(ids_asientos)

        subtotal_snacks = 0.0
        detalle_confiteria = []
        for snack_item in payload.snacks:
            producto = db.get(ProductoConfiteria, snack_item.id_producto)
            if not producto:
                raise HTTPException(status_code=404, detail=f"Snack no encontrado: {snack_item.id_producto}")

            if snack_item.cantidad <= 0:
                raise HTTPException(status_code=400, detail="La cantidad del snack debe ser mayor a cero")

            if producto.stock is not None and producto.stock < snack_item.cantidad:
                raise HTTPException(status_code=409, detail=f"Stock insuficiente para {producto.nombre_producto}")

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

        resultado_pago = payment_gateway_service.cobrar(payload.token_pago, monto_total, payload.email)
        if not resultado_pago["aprobado"]:
            raise HTTPException(status_code=402, detail=resultado_pago["mensaje"])

        if has_seats:
            set_showtime_seats_state(db, payload.id_funcion, ids_asientos, "Ocupado")

            db.query(BloqueoTemporal).filter(
                BloqueoTemporal.id_funcion == payload.id_funcion,
                BloqueoTemporal.id_asiento.in_(ids_asientos),
            ).delete(synchronize_session=False)

        transaccion = Transaccion(
            id_usuario=payload.id_usuario,
            id_funcion=payload.id_funcion if has_seats else None,
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

        for snack_item in payload.snacks:
            producto = db.get(ProductoConfiteria, snack_item.id_producto)
            if producto and producto.stock is not None:
                producto.stock = max(0, producto.stock - snack_item.cantidad)

        db.flush()

        pelicula = funcion.pelicula if funcion else None
        evento = HistorialActividad(
            id_usuario=payload.id_usuario,
            tipo_evento="COMPRA",
            id_referencia_pelicula=funcion.id_pelicula if funcion else None,
            texto_breve=(
                f"Compro {len(ids_asientos)} boleto(s) para {pelicula.titulo if pelicula else ''}"
                if has_seats
                else "Compro dulceria"
            ),
        )
        db.add(evento)

        qr_payload = build_ticket_qr_payload(transaccion, funcion, seat_rows, tickets) if has_seats else None

    if has_seats:
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

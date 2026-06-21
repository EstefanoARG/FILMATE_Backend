import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.models.cinema import Cine
from app.models.transaccion import Transaccion
from app.models.room import Sala
from app.models.seat import Asiento
from app.models.showtime import Funcion
from app.models.boleta_ticket import BoletaTicket
from app.schemas.ticket import TicketQrPayload


def _build_ticket_data(ticket: BoletaTicket, asiento: Asiento | None) -> Dict[str, Any]:
    return {
        "id_ticket": ticket.id_ticket,
        "id_asiento": asiento.id_asiento if asiento else None,
        "fila": asiento.fila if asiento else None,
        "columna": asiento.columna if asiento else None,
        "codigo_qr_token": ticket.codigo_qr_token,
        "estado_ticket": ticket.estado_ticket,
    }


def _build_tickets_data(asientos: List[Asiento], tickets: List[BoletaTicket]) -> List[Dict[str, Any]]:
    return [_build_ticket_data(ticket, asientos[i] if i < len(asientos) else None) for i, ticket in enumerate(tickets)]


def _build_cine_info(cine: Cine | None) -> Dict[str, Any]:
    return {
        "id_cine": cine.id_cine if cine else None,
        "nombre_cine": cine.nombre_cine if cine else None,
    }


def _build_sala_info(sala: Sala | None) -> Dict[str, Any]:
    return {
        "id_sala": sala.id_sala if sala else None,
        "nombre_sala": sala.nombre_sala if sala else None,
    }


def _build_pelicula_info(pelicula: Any) -> Dict[str, Any]:
    return {
        "id_pelicula": pelicula.id_pelicula if pelicula else None,
        "titulo": pelicula.titulo if pelicula else None,
    }


def build_ticket_qr_payload(
    transaccion: Transaccion,
    funcion: Funcion,
    asientos: List[Asiento],
    tickets: List[BoletaTicket],
) -> TicketQrPayload:
    pelicula = funcion.pelicula
    sala = funcion.sala
    cine = sala.cine if sala else None

    txn_data: Dict[str, Any] = {
        "id_transaccion": transaccion.id_transaccion,
        "id_usuario": transaccion.id_usuario,
        "id_funcion": transaccion.id_funcion,
        "monto_boletos": float(transaccion.monto_boletos),
        "monto_confiteria": float(transaccion.monto_confiteria),
        "monto_total": float(transaccion.monto_total),
        "estado_pago": transaccion.estado_pago,
        "metodo_pago": transaccion.metodo_pago,
        "fecha_transaccion": transaccion.fecha_transaccion,
    }

    tickets_data = _build_tickets_data(asientos, tickets)

    payload = {
        "version": "1.0",
        "generado_en": datetime.now(timezone.utc),
        "transaccion": txn_data,
        "cine": _build_cine_info(cine),
        "sala": _build_sala_info(sala),
        "funcion": {
            "id_funcion": funcion.id_funcion,
            "fecha_hora": funcion.fecha_hora,
            "precio_base": float(funcion.precio_base),
        },
        "pelicula": _build_pelicula_info(pelicula),
        "boletos": tickets_data,
    }

    return TicketQrPayload(
        version="1.0",
        generado_en=datetime.now(timezone.utc),
        transaccion=txn_data,
        boletos=tickets_data,
        payload_json=json.dumps(payload, ensure_ascii=False, default=str),
    )

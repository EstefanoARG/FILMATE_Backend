import json
from datetime import datetime
from typing import Any, Dict, List

from app.models.cinema import Cine
from app.models.transaccion import Transaccion
from app.models.room import Sala
from app.models.seat import Asiento
from app.models.showtime import Funcion
from app.models.boleta_ticket import BoletaTicket
from app.schemas.ticket import TicketQrPayload


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

    tickets_data = []
    for i, ticket in enumerate(tickets):
        asiento = asientos[i] if i < len(asientos) else None
        tickets_data.append({
            "id_ticket": ticket.id_ticket,
            "id_asiento": asiento.id_asiento if asiento else None,
            "fila": asiento.fila if asiento else None,
            "columna": asiento.columna if asiento else None,
            "codigo_qr_token": ticket.codigo_qr_token,
            "estado_ticket": ticket.estado_ticket,
        })

    payload = {
        "version": "1.0",
        "generado_en": datetime.utcnow(),
        "transaccion": txn_data,
        "cine": {
            "id_cine": cine.id_cine if cine else None,
            "nombre_cine": cine.nombre_cine if cine else None,
        },
        "sala": {
            "id_sala": sala.id_sala if sala else None,
            "nombre_sala": sala.nombre_sala if sala else None,
        },
        "funcion": {
            "id_funcion": funcion.id_funcion,
            "fecha_hora": funcion.fecha_hora,
            "precio_base": float(funcion.precio_base),
        },
        "pelicula": {
            "id_pelicula": pelicula.id_pelicula if pelicula else None,
            "titulo": pelicula.titulo if pelicula else None,
        },
        "boletos": tickets_data,
    }

    return TicketQrPayload(
        version="1.0",
        generado_en=datetime.utcnow(),
        transaccion=txn_data,
        boletos=tickets_data,
        payload_json=json.dumps(payload, ensure_ascii=False, default=str),
    )

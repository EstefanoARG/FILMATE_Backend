from datetime import datetime, timedelta

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.movie import Pelicula
from app.models.reservation import Reserva
from app.models.reservation_snack import ReservaSnack
from app.models.room import Sala
from app.models.seat import Asiento
from app.models.showtime import Funcion
from app.models.snack_product import ProductoSnack
from app.models.ticket import Boleto
from app.models.user import Usuario


def list_transactions(
    db: Session,
    tipo: str = None,
    estado: str = None,
    fecha: str = None,
    buscar: str = None,
    page: int = 1,
    limit: int = 10
):

    query = (
        db.query(
            Reserva,
            Usuario,
            Funcion,
            Pelicula,
            Sala
        )
        .join(
            Usuario,
            Usuario.id_usuario == Reserva.id_usuario
        )
        .join(
            Funcion,
            Funcion.id_funcion == Reserva.id_funcion
        )
        .join(
            Pelicula,
            Pelicula.id_pelicula == Funcion.id_pelicula
        )
        .join(
            Sala,
            Sala.id_sala == Funcion.id_sala
        )
    )

    # FILTRO ESTADO
    if estado:
        query = query.filter(
            Reserva.estado_pago == estado
        )

    # FILTRO FECHA
    if fecha:

        dias_map = {
            "1d": 1,
            "7d": 7,
            "30d": 30
        }

        dias = dias_map.get(fecha)

        if dias:

            fecha_limite = (
                datetime.now() - timedelta(days=dias)
            )

            query = query.filter(
                Reserva.fecha_reserva >= fecha_limite
            )

    # FILTRO BÚSQUEDA
    if buscar:

        query = query.filter(
            or_(
                Pelicula.titulo.ilike(
                    f"%{buscar}%"
                ),

                Usuario.nombres.ilike(
                    f"%{buscar}%"
                ),

                Usuario.apellidos.ilike(
                    f"%{buscar}%"
                ),

                Reserva.transaccion_id.ilike(
                    f"%{buscar}%"
                )
            )
        )

    total = query.count()

    results = (
        query
        .order_by(
            Reserva.fecha_reserva.desc()
        )
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    transactions = []

    for (reserva, usuario, funcion, pelicula, sala) in results:

        # Contar boletos y snacks para esta reserva
        num_boletos = (
            db.query(func.count(Boleto.id_boleto))
            .filter(Boleto.id_reserva == reserva.id_reserva)
            .scalar()
        )

        num_snacks = (
            db.query(func.count(ReservaSnack.id_producto))
            .filter(ReservaSnack.id_reserva == reserva.id_reserva)
            .scalar()
        )

        total_snacks = float(
            db.query(func.coalesce(func.sum(ReservaSnack.subtotal), 0))
            .filter(ReservaSnack.id_reserva == reserva.id_reserva)
            .scalar()
        )
        monto_real = float(reserva.monto_total)

        # Determinar tipo
        if num_boletos > 0 and num_snacks > 0:
            tipo = 'Entrada + Dulcería'
        elif num_snacks > 0:
            tipo = 'Solo Dulcería'
        else:
            tipo = 'Solo Entrada'

        transactions.append({
            "id_reserva":   reserva.id_reserva,
            "transaccion_id": reserva.transaccion_id,
            "cliente":      f"{usuario.nombres} {usuario.apellidos}",
            "pelicula":     pelicula.titulo,
            "sala":         sala.nombre,
            "monto_total":  monto_real,
            "estado_pago":  reserva.estado_pago,
            "metodo_pago":  reserva.metodo_pago,
            "fecha_compra": reserva.fecha_reserva,
            "tipo":         tipo,   # ← nuevo campo
        })

    ingresos_reservas = float(
        db.query(func.coalesce(func.sum(Reserva.monto_total), 0))
        .scalar()
    )

    ingresos_snacks = float(
        db.query(func.coalesce(func.sum(ReservaSnack.subtotal), 0))
        .scalar()
    )

    ingresos_totales = ingresos_reservas + ingresos_snacks

    ventas_mes = (
        db.query(func.count(Reserva.id_reserva))
        .filter(Reserva.estado_pago == "Pagado")
        .scalar()
    )

    ticket_promedio = (
        ingresos_reservas / ventas_mes
        if ventas_mes > 0
        else 0
    )

    return {
        "data": transactions,

        "total": total,

        "page": page,

        "totalPages": (
            (total + limit - 1) // limit
        ),

        "metricas": {

            "ventasMes": ventas_mes,

            "ingresosTotales": (
                float(ingresos_totales)
            ),

            "reembolsos": 0,

            "ticketPromedio": round(
                ticket_promedio,
                2
            )
        }
    }


def get_transaction_detail(
    db: Session,
    reservation_id: int
):

    row = (
        db.query(
            Reserva,
            Usuario,
            Funcion,
            Pelicula,
            Sala
        )
        .join(
            Usuario,
            Usuario.id_usuario == Reserva.id_usuario
        )
        .join(
            Funcion,
            Funcion.id_funcion == Reserva.id_funcion
        )
        .join(
            Pelicula,
            Pelicula.id_pelicula == Funcion.id_pelicula
        )
        .join(
            Sala,
            Sala.id_sala == Funcion.id_sala
        )
        .filter(
            Reserva.id_reserva == reservation_id
        )
        .first()
    )

    if not row:
        return None

    (
        reserva,
        usuario,
        funcion,
        pelicula,
        sala
    ) = row

    # BOLETOS
    boletos_query = (
        db.query(
            Boleto,
            Asiento
        )
        .join(
            Asiento,
            Asiento.id_asiento
            == Boleto.id_asiento
        )
        .filter(
            Boleto.id_reserva
            == reservation_id
        )
        .all()
    )

    boletos = []

    for boleto, asiento in boletos_query:

        boletos.append({

            "id_boleto": boleto.id_boleto,

            "asiento": (
                f"{asiento.fila}"
                f"{asiento.numero}"
            ),

            "precio_pagado": (
                boleto.precio_pagado
            ),

            "estado_ingreso": (
                boleto.estado_ingreso
            ),

            "codigo_qr": boleto.codigo_qr
        })

    # SNACKS
    snacks_query = (
        db.query(
            ReservaSnack,
            ProductoSnack
        )
        .outerjoin(
            ProductoSnack,
            ProductoSnack.id_producto
            == ReservaSnack.id_producto
        )
        .filter(
            ReservaSnack.id_reserva
            == reservation_id
        )
        .all()
    )

    snacks = []

    for rs, producto in snacks_query:
        subtotal = float(rs.subtotal) if rs.subtotal is not None else float(rs.cantidad * rs.precio_unitario)
        nombre_producto = producto.nombre if producto else "Producto eliminado"

        snacks.append({

            "producto": nombre_producto,

            "cantidad": rs.cantidad,

            "subtotal": subtotal
        })

    return {

        "id_reserva": reserva.id_reserva,

        "cliente": (
            f"{usuario.nombres} "
            f"{usuario.apellidos}"
        ),

        "correo": usuario.correo,

        "pelicula": pelicula.titulo,

        "sala": sala.nombre,

        "funcion": {
            "id_funcion": funcion.id_funcion,
            "fecha_inicio": (
                funcion.fecha_hora_inicio
            ),
            "fecha_fin": (
                funcion.fecha_hora_fin
            ),
            "idioma": funcion.idioma,
            "formato": funcion.formato
        },

        "monto_subtotal": (
            reserva.monto_subtotal
        ),

        "descuento_aplicado": (
            reserva.descuento_aplicado
        ),

        "monto_total": (
            reserva.monto_total
        ),

        "estado_pago": (
            reserva.estado_pago
        ),

        "metodo_pago": (
            reserva.metodo_pago
        ),

        "transaccion_id": (
            reserva.transaccion_id
        ),

        "fecha_reserva": (
            reserva.fecha_reserva
        ),

        "boletos": boletos,

        "snacks": snacks
    }


def validate_ticket_or_transaction(
    db: Session,
    codigo_qr: str = None,
    codigo: str = None
):

    # VALIDACIÓN QR
    if codigo_qr:

        boleto = (
            db.query(Boleto)
            .filter(
                Boleto.codigo_qr == codigo_qr
            )
            .first()
        )

        if not boleto:

            return {
                "valido": False,
                "estado": "Inválida"
            }

        if boleto.estado_ingreso == "Usado":

            return {
                "valido": False,
                "estado": "Ya Usada"
            }

        boleto.estado_ingreso = "Usado"

        db.commit()

        return {

            "valido": True,

            "estado": "Válida",

            "detalle": {

                "id_boleto": (
                    boleto.id_boleto
                ),

                "codigo_qr": (
                    boleto.codigo_qr
                )
            }
        }

    # VALIDACIÓN TRANSACCIÓN
    if codigo:

        reserva = (
            db.query(Reserva)
            .filter(
                Reserva.transaccion_id
                == codigo
            )
            .first()
        )

        if not reserva:

            return {
                "valido": False,
                "estado": "Inválida"
            }

        return {

            "valido": True,

            "estado": "Válida",

            "detalle": {

                "id_reserva": (
                    reserva.id_reserva
                ),

                "transaccion_id": (
                    reserva.transaccion_id
                )
            }
        }

    return {
        "valido": False,
        "estado": "Inválida"
    }
from datetime import datetime, timedelta

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.movie import Pelicula
from app.models.transaccion import Transaccion
from app.models.detalle_boleta_asiento import DetalleBoletaAsiento
from app.models.detalle_boleta_confiteria import DetalleBoletaConfiteria
from app.models.room import Sala
from app.models.seat import Asiento
from app.models.showtime import Funcion
from app.models.snack_product import ProductoConfiteria
from app.models.boleta_ticket import BoletaTicket
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
        db.query(Transaccion, Usuario, Funcion, Pelicula, Sala)
        .join(Usuario, Usuario.id_usuario == Transaccion.id_usuario)
        .join(Funcion, Funcion.id_funcion == Transaccion.id_funcion)
        .join(Pelicula, Pelicula.id_pelicula == Funcion.id_pelicula)
        .join(Sala, Sala.id_sala == Funcion.id_sala)
    )

    if estado:
        query = query.filter(Transaccion.estado_pago == estado)

    if fecha:
        dias_map = {"1d": 1, "7d": 7, "30d": 30}
        dias = dias_map.get(fecha)
        if dias:
            query = query.filter(Transaccion.fecha_transaccion >= datetime.now() - timedelta(days=dias))

    if buscar:
        query = query.filter(
            or_(
                Pelicula.titulo.ilike(f"%{buscar}%"),
                Usuario.nombre.ilike(f"%{buscar}%"),
            )
        )

    total = query.count()
    results = query.order_by(Transaccion.fecha_transaccion.desc()).offset((page - 1) * limit).limit(limit).all()

    transactions = []
    for txn, usuario, funcion, pelicula, sala in results:
        num_boletos = db.query(func.count(DetalleBoletaAsiento.id_detalle_asiento)).filter(
            DetalleBoletaAsiento.id_transaccion == txn.id_transaccion
        ).scalar()

        num_snacks = db.query(func.count(DetalleBoletaConfiteria.id_detalle_confi)).filter(
            DetalleBoletaConfiteria.id_transaccion == txn.id_transaccion
        ).scalar()

        if num_boletos and num_snacks:
            tipo_str = "Entrada + Dulcería"
        elif num_snacks:
            tipo_str = "Solo Dulcería"
        else:
            tipo_str = "Solo Entrada"

        transactions.append({
            "id_transaccion": txn.id_transaccion,
            "cliente": usuario.nombre,
            "pelicula": pelicula.titulo,
            "sala": sala.nombre_sala,
            "monto_total": float(txn.monto_total),
            "estado_pago": txn.estado_pago,
            "metodo_pago": txn.metodo_pago,
            "fecha_transaccion": txn.fecha_transaccion,
            "tipo": tipo_str,
        })

    ingresos_totales = float(
        db.query(func.coalesce(func.sum(Transaccion.monto_total), 0))
        .filter(Transaccion.estado_pago == "Aprobado")
        .scalar()
    )

    ventas_mes = db.query(func.count(Transaccion.id_transaccion)).filter(
        Transaccion.estado_pago == "Aprobado"
    ).scalar()

    ticket_promedio = ingresos_totales / ventas_mes if ventas_mes > 0 else 0

    reembolsos = db.query(func.count(Transaccion.id_transaccion)).filter(
        Transaccion.estado_pago == "Reembolsada"
    ).scalar()

    return {
        "data": transactions,
        "total": total,
        "page": page,
        "totalPages": (total + limit - 1) // limit if total else 1,
        "metricas": {
            "ventasMes": ventas_mes,
            "ingresosTotales": ingresos_totales,
            "reembolsos": reembolsos,
            "ticketPromedio": round(ticket_promedio, 2),
        },
    }


def get_transaction_detail(db: Session, transaction_id: int):
    row = (
        db.query(Transaccion, Usuario, Funcion, Pelicula, Sala)
        .join(Usuario, Usuario.id_usuario == Transaccion.id_usuario)
        .join(Funcion, Funcion.id_funcion == Transaccion.id_funcion)
        .join(Pelicula, Pelicula.id_pelicula == Funcion.id_pelicula)
        .join(Sala, Sala.id_sala == Funcion.id_sala)
        .filter(Transaccion.id_transaccion == transaction_id)
        .first()
    )

    if not row:
        return None

    txn, usuario, _, pelicula, sala = row

    boletos_query = (
        db.query(DetalleBoletaAsiento, Asiento)
        .join(Asiento, Asiento.id_asiento == DetalleBoletaAsiento.id_asiento)
        .filter(DetalleBoletaAsiento.id_transaccion == transaction_id)
        .all()
    )

    boletos = []
    for dba, asiento in boletos_query:
        boletos.append({
            "id_detalle_asiento": dba.id_detalle_asiento,
            "asiento": f"{asiento.fila}{asiento.columna}",
            "ingresado": dba.ingresado,
        })

    snacks_query = (
        db.query(DetalleBoletaConfiteria, ProductoConfiteria)
        .outerjoin(ProductoConfiteria, ProductoConfiteria.id_producto == DetalleBoletaConfiteria.id_producto)
        .filter(DetalleBoletaConfiteria.id_transaccion == transaction_id)
        .all()
    )

    snacks = []
    for dbc, producto in snacks_query:
        snacks.append({
            "producto": producto.nombre_producto if producto else "Producto eliminado",
            "cantidad": dbc.cantidad,
            "subtotal": float(dbc.cantidad * dbc.precio_unitario),
        })

    return {
        "id_transaccion": txn.id_transaccion,
        "cliente": usuario.nombre,
        "correo": usuario.correo,
        "pelicula": pelicula.titulo,
        "sala": sala.nombre_sala,
        "monto_boletos": float(txn.monto_boletos),
        "monto_confiteria": float(txn.monto_confiteria),
        "monto_total": float(txn.monto_total),
        "estado_pago": txn.estado_pago,
        "metodo_pago": txn.metodo_pago,
        "fecha_transaccion": txn.fecha_transaccion,
        "boletos": boletos,
        "snacks": snacks,
    }


def validate_ticket_or_transaction(db: Session, codigo_qr_token: str = None):
    if codigo_qr_token:
        ticket = db.query(BoletaTicket).filter(BoletaTicket.codigo_qr_token == codigo_qr_token).first()
        if not ticket:
            return {"valido": False, "estado": "Inválida"}
        if ticket.estado_ticket != "Valido":
            return {"valido": False, "estado": "Ya Usada"}
        ticket.estado_ticket = "Canjeado"
        db.commit()
        return {"valido": True, "estado": "Válida", "detalle": {"id_ticket": ticket.id_ticket}}

    return {"valido": False, "estado": "Inválida"}

import re
from datetime import datetime, timedelta

from sqlalchemy import func, or_, and_, exists
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
from app.models.cinema import Cine


def _build_fecha_filter(fecha: str = None):
    if not fecha:
        return True
    ahora = datetime.now()
    if fecha == "mes_anterior":
        inicio = (ahora.replace(day=1) - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fin = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return and_(
            Transaccion.fecha_transaccion >= inicio,
            Transaccion.fecha_transaccion < fin,
        )
    dias_map = {"1d": 1, "7d": 7, "30d": 30}
    dias = dias_map.get(fecha)
    if dias:
        return Transaccion.fecha_transaccion >= ahora - timedelta(days=dias)
    return True


def list_transactions(
    db: Session,
    tipo: str = None,
    estado: str = None,
    fecha: str = None,
    buscar: str = None,
    page: int = 1,
    limit: int = 10
):
    fecha_filter = _build_fecha_filter(fecha)

    query = (
        db.query(Transaccion, Usuario, Funcion, Pelicula, Sala)
        .join(Usuario, Usuario.id_usuario == Transaccion.id_usuario)
        .join(Funcion, Funcion.id_funcion == Transaccion.id_funcion)
        .join(Pelicula, Pelicula.id_pelicula == Funcion.id_pelicula)
        .join(Sala, Sala.id_sala == Funcion.id_sala)
    )

    if estado:
        query = query.filter(Transaccion.estado_pago == estado)

    if fecha_filter is not True:
        query = query.filter(fecha_filter)

    if buscar:
        buscar_filters = [
            Pelicula.titulo.ilike(f"%{buscar}%"),
            Usuario.nombre.ilike(f"%{buscar}%"),
            Usuario.documento.ilike(f"%{buscar}%"),
        ]
        try:
            buscar_id = int(buscar)
            buscar_filters.append(Transaccion.id_transaccion == buscar_id)
        except ValueError:
            pass

        query = query.filter(or_(*buscar_filters))

    if tipo:
        has_boletos = exists().where(DetalleBoletaAsiento.id_transaccion == Transaccion.id_transaccion)
        has_snacks = exists().where(DetalleBoletaConfiteria.id_transaccion == Transaccion.id_transaccion)

        if tipo == "Solo Entrada":
            query = query.filter(and_(has_boletos, ~has_snacks))
        elif tipo == "Solo Dulcería":
            query = query.filter(and_(~has_boletos, has_snacks))
        elif tipo == "Entrada + Dulcería":
            query = query.filter(and_(has_boletos, has_snacks))

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

    metrics_base = db.query(func.coalesce(func.sum(Transaccion.monto_total), 0))
    metrics_count = db.query(func.count(Transaccion.id_transaccion))

    if fecha_filter is not True:
        metrics_base = metrics_base.filter(fecha_filter)
        metrics_count = metrics_count.filter(fecha_filter)

    ingresos_totales = float(
        metrics_base.filter(Transaccion.estado_pago == "Aprobado").scalar()
    )

    ventas_mes = metrics_count.filter(
        Transaccion.estado_pago == "Aprobado"
    ).scalar()

    ticket_promedio = ingresos_totales / ventas_mes if ventas_mes > 0 else 0

    reembolsos = metrics_count.filter(
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
        db.query(Transaccion, Usuario, Funcion, Pelicula, Sala, Cine)
        .join(Usuario, Usuario.id_usuario == Transaccion.id_usuario)
        .join(Funcion, Funcion.id_funcion == Transaccion.id_funcion)
        .join(Pelicula, Pelicula.id_pelicula == Funcion.id_pelicula)
        .join(Sala, Sala.id_sala == Funcion.id_sala)
        .join(Cine, Cine.id_cine == Sala.id_cine)
        .filter(Transaccion.id_transaccion == transaction_id)
        .first()
    )

    if not row:
        return None

    txn, usuario, funcion, pelicula, sala, cine = row

    boletos_query = (
        db.query(DetalleBoletaAsiento, Asiento)
        .join(Asiento, Asiento.id_asiento == DetalleBoletaAsiento.id_asiento)
        .filter(DetalleBoletaAsiento.id_transaccion == transaction_id)
        .all()
    )

    precio_por_asiento = float(funcion.precio_base) if funcion.precio_base else 0

    boletos = []
    for dba, asiento in boletos_query:
        boletos.append({
            "id_detalle_asiento": dba.id_detalle_asiento,
            "asiento": f"{asiento.fila}{asiento.columna}",
            "ingresado": dba.ingresado,
            "precio": precio_por_asiento,
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
        "id_cine": cine.id_cine,
        "nombre_cine": cine.nombre_cine,
        "fecha_hora_funcion": funcion.fecha_hora,
        "monto_boletos": float(txn.monto_boletos),
        "monto_confiteria": float(txn.monto_confiteria),
        "monto_total": float(txn.monto_total),
        "estado_pago": txn.estado_pago,
        "metodo_pago": txn.metodo_pago,
        "fecha_transaccion": txn.fecha_transaccion,
        "boletos": boletos,
        "snacks": snacks,
    }


def validate_ticket_or_transaction(db: Session, codigo_qr_token: str = None, codigo: str = None):
    code = codigo_qr_token or codigo
    if not code:
        return {"valido": False, "estado": "Inválida"}

    match = re.match(r'^QR-FILMATE-TXN(\d+)-(\d+)$', code)
    if match:
        id_transaccion = int(match.group(1))
        id_detalle_asiento = int(match.group(2))
        detalle = db.query(DetalleBoletaAsiento).filter(
            DetalleBoletaAsiento.id_detalle_asiento == id_detalle_asiento,
            DetalleBoletaAsiento.id_transaccion == id_transaccion,
        ).first()
        if not detalle:
            return {"valido": False, "estado": "Inválida"}
        if detalle.ingresado:
            return {"valido": False, "estado": "Ya Usada"}
        detalle.ingresado = True
        db.commit()

        txn = db.query(Transaccion).filter(Transaccion.id_transaccion == id_transaccion).first()
        usuario = db.query(Usuario).filter(Usuario.id_usuario == txn.id_usuario).first() if txn else None
        asiento_obj = db.query(Asiento).filter(Asiento.id_asiento == detalle.id_asiento).first()
        return {
            "valido": True, "estado": "Válida",
            "detalle": {"id_detalle_asiento": id_detalle_asiento},
            "cliente": usuario.nombre if usuario else '—',
            "asiento": f"{asiento_obj.fila}{asiento_obj.columna}" if asiento_obj else '—',
        }

    ticket = db.query(BoletaTicket).filter(
        or_(
            BoletaTicket.codigo_qr_token == code,
            BoletaTicket.id_ticket == (int(code) if code.isdigit() else -1),
        )
    ).first()

    if not ticket:
        return {"valido": False, "estado": "Inválida"}
    if ticket.estado_ticket != "Valido":
        return {"valido": False, "estado": "Ya Usada"}
    ticket.estado_ticket = "Canjeado"
    db.commit()

    txn = db.query(Transaccion).filter(Transaccion.id_transaccion == ticket.id_transaccion).first()
    usuario = db.query(Usuario).filter(Usuario.id_usuario == txn.id_usuario).first() if txn else None
    detalle_asiento = db.query(DetalleBoletaAsiento).filter(
        DetalleBoletaAsiento.id_transaccion == ticket.id_transaccion
    ).first()
    asiento_obj = db.query(Asiento).filter(Asiento.id_asiento == detalle_asiento.id_asiento).first() if detalle_asiento else None
    return {
        "valido": True, "estado": "Válida",
        "detalle": {"id_ticket": ticket.id_ticket},
        "cliente": usuario.nombre if usuario else '—',
        "asiento": f"{asiento_obj.fila}{asiento_obj.columna}" if asiento_obj else '—',
    }

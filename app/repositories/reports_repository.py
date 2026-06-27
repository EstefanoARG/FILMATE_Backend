from datetime import datetime, timedelta

from sqlalchemy import and_, case, func
from sqlalchemy.orm import Session

from app.models.cinema import Cine
from app.models.detalle_boleta_asiento import DetalleBoletaAsiento
from app.models.detalle_boleta_confiteria import DetalleBoletaConfiteria
from app.models.genre import Genero
from app.models.movie import Pelicula
from app.models.movie_genre import PeliculaGenero
from app.models.reporte_contador import ReporteContador
from app.models.room import Sala
from app.models.showtime import Funcion
from app.models.showtime_seat import AsientoFuncion
from app.models.snack_product import ProductoConfiteria
from app.models.transaccion import Transaccion
from app.models.user import Usuario


def _get_periodo_fechas(periodo: str, hoy: datetime = None):
    if hoy is None:
        hoy = datetime.now()
    if periodo == "mes_anterior":
        inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fin = inicio_mes
        inicio = (inicio_mes - timedelta(days=1)).replace(day=1)
        return inicio, fin
    inicio_map = {
        "hoy": hoy.replace(hour=0, minute=0, second=0, microsecond=0),
        "semana": (hoy - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0),
        "mes": (hoy - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0),
        "anio": (hoy - timedelta(days=365)).replace(hour=0, minute=0, second=0, microsecond=0),
    }
    inicio = inicio_map.get(periodo, inicio_map["mes"])
    return inicio, None


def _filter_fecha_range(query, model_col, inicio, fin):
    if fin is not None:
        return query.filter(model_col >= inicio, model_col < fin)
    return query.filter(model_col >= inicio)


def get_taquilla_data(db: Session, periodo: str):
    hoy = datetime.now()
    inicio, fin = _get_periodo_fechas(periodo, hoy)

    query = (
        db.query(
            Pelicula.id_pelicula.label("id"),
            Pelicula.titulo,
            func.count(func.distinct(Funcion.id_funcion)).label("funciones"),
            func.count(DetalleBoletaAsiento.id_detalle_asiento).label("entradas"),
            func.coalesce(func.sum(Transaccion.monto_total), 0).label("ingreso"),
            Pelicula.estado_pelicula.label("estado"),
        )
        .join(Funcion, Pelicula.id_pelicula == Funcion.id_pelicula)
        .join(Transaccion, Funcion.id_funcion == Transaccion.id_funcion)
        .join(
            DetalleBoletaAsiento,
            Transaccion.id_transaccion == DetalleBoletaAsiento.id_transaccion,
        )
        .filter(Transaccion.estado_pago == "Aprobado")
    )
    query = _filter_fecha_range(query, Transaccion.fecha_transaccion, inicio, fin)
    rows = (
        query
        .group_by(Pelicula.id_pelicula, Pelicula.titulo, Pelicula.estado_pelicula)
        .order_by(func.coalesce(func.sum(Transaccion.monto_total), 0).desc())
        .all()
    )

    data = [
        {
            "id": r.id,
            "titulo": r.titulo,
            "funciones": r.funciones,
            "entradas": r.entradas,
            "ingreso": float(r.ingreso),
            "estado": r.estado,
        }
        for r in rows
    ]

    total_funciones = sum(r["funciones"] for r in data)
    total_entradas = sum(r["entradas"] for r in data)
    ingreso_bruto = sum(r["ingreso"] for r in data)
    ticket_promedio = round(ingreso_bruto / total_entradas, 2) if total_entradas else 0.0

    return {
        "data": data,
        "resumen": {
            "total_funciones": total_funciones,
            "total_entradas": total_entradas,
            "ingreso_bruto": round(ingreso_bruto, 2),
            "ticket_promedio": ticket_promedio,
        },
    }


def get_ocupacion_salas_data(db: Session, periodo: str):
    hoy = datetime.now()
    inicio, fin = _get_periodo_fechas(periodo, hoy)

    vendidos_col = func.count(
        case((AsientoFuncion.estado == "Ocupado", 1))
    )
    funciones_distintas = func.count(func.distinct(Funcion.id_funcion))
    denom = func.nullif(
        Sala.capacidad_asientos * funciones_distintas, 0
    )
    porcentaje_col = func.round(vendidos_col * 100.0 / denom, 1)

    funcion_cond = [Funcion.id_sala == Sala.id_sala, Funcion.fecha_hora >= inicio]
    if fin is not None:
        funcion_cond.append(Funcion.fecha_hora < fin)

    query = (
        db.query(
            Sala.id_sala,
            Sala.nombre_sala.label("sala"),
            Sala.id_cine,
            Cine.nombre_cine.label("cine"),
            Sala.capacidad_asientos.label("capacidad"),
            vendidos_col.label("vendidos"),
            porcentaje_col.label("porcentaje"),
            Sala.tipo_formato.label("formato"),
        )
        .join(Cine, Cine.id_cine == Sala.id_cine)
        .outerjoin(Funcion, and_(*funcion_cond))
        .outerjoin(
            AsientoFuncion, AsientoFuncion.id_funcion == Funcion.id_funcion
        )
        .group_by(
            Sala.id_sala,
            Sala.nombre_sala,
            Sala.id_cine,
            Cine.nombre_cine,
            Sala.capacidad_asientos,
            Sala.tipo_formato,
        )
        .order_by(porcentaje_col.desc())
    )

    rows = query.all()

    data = [
        {
            "id_sala": r.id_sala,
            "sala": r.sala,
            "id_cine": r.id_cine,
            "cine": r.cine,
            "capacidad": r.capacidad,
            "vendidos": r.vendidos,
            "porcentaje": float(r.porcentaje) if r.porcentaje is not None else 0.0,
            "formato": r.formato,
        }
        for r in rows
    ]

    total_salas = len(data)
    capacidad_total = sum(r["capacidad"] for r in data)
    ocupacion_promedio = (
        round(sum(r["porcentaje"] for r in data) / total_salas, 1)
        if total_salas
        else 0.0
    )

    return {
        "data": data,
        "resumen": {
            "total_salas": total_salas,
            "capacidad_total": capacidad_total,
            "ocupacion_promedio": ocupacion_promedio,
        },
    }


def get_ventas_horario_data(db: Session, periodo: str):
    hoy = datetime.now()
    inicio, fin = _get_periodo_fechas(periodo, hoy)

    horario_case = case(
        (func.hour(Transaccion.fecha_transaccion).between(10, 11), "10:00 - 12:00"),
        (func.hour(Transaccion.fecha_transaccion).between(12, 13), "12:00 - 14:00"),
        (func.hour(Transaccion.fecha_transaccion).between(14, 15), "14:00 - 16:00"),
        (func.hour(Transaccion.fecha_transaccion).between(16, 17), "16:00 - 18:00"),
        (func.hour(Transaccion.fecha_transaccion).between(18, 19), "18:00 - 20:00"),
        (func.hour(Transaccion.fecha_transaccion).between(20, 21), "20:00 - 22:00"),
        else_="Otro",
    ).label("horario")

    query = (
        db.query(
            horario_case,
            func.count(func.distinct(Transaccion.id_transaccion)).label("ventas"),
            func.coalesce(func.sum(Transaccion.monto_total), 0).label("ingresos"),
            func.count(DetalleBoletaAsiento.id_detalle_asiento).label("tickets"),
        )
        .outerjoin(
            DetalleBoletaAsiento,
            Transaccion.id_transaccion == DetalleBoletaAsiento.id_transaccion,
        )
        .filter(Transaccion.estado_pago == "Aprobado")
    )
    query = _filter_fecha_range(query, Transaccion.fecha_transaccion, inicio, fin)
    query = query.group_by("horario").order_by(func.min(func.hour(Transaccion.fecha_transaccion)))

    rows = query.all()

    data = [
        {
            "horario": r.horario,
            "ventas": r.ventas,
            "ingresos": float(r.ingresos),
            "tickets": r.tickets,
        }
        for r in rows
    ]

    total_ingresos = sum(r["ingresos"] for r in data)
    total_tickets = sum(r["tickets"] for r in data)
    horario_pico = max(data, key=lambda x: x["ingresos"])["horario"] if data else ""

    return {
        "data": data,
        "resumen": {
            "horario_pico": horario_pico,
            "ingreso_total": round(total_ingresos, 2),
            "total_tickets": total_tickets,
        },
    }


def get_analisis_peliculas_data(db: Session, periodo: str):
    hoy = datetime.now()
    inicio, fin = _get_periodo_fechas(periodo, hoy)

    subq_filter = [Transaccion.estado_pago == "Aprobado", Transaccion.fecha_transaccion >= inicio]
    if fin is not None:
        subq_filter.append(Transaccion.fecha_transaccion < fin)

    total_ingresos_subq = (
        db.query(func.coalesce(func.sum(Transaccion.monto_total), 0))
        .filter(*subq_filter)
        .scalar_subquery()
    )

    funcion_cond = [Funcion.id_pelicula == Pelicula.id_pelicula, Funcion.fecha_hora >= inicio]
    transaccion_cond = [Transaccion.id_funcion == Funcion.id_funcion, Transaccion.fecha_transaccion >= inicio]
    if fin is not None:
        funcion_cond.append(Funcion.fecha_hora < fin)
        transaccion_cond.append(Transaccion.fecha_transaccion < fin)

    rows = (
        db.query(
            Genero.id_genero,
            Genero.nombre_genero.label("genero"),
            func.count(func.distinct(Pelicula.id_pelicula)).label("peliculas"),
            func.count(func.distinct(Funcion.id_funcion)).label("funciones"),
            func.coalesce(func.sum(Transaccion.monto_total), 0).label("ingresos"),
            func.round(
                func.coalesce(func.sum(Transaccion.monto_total), 0)
                * 100.0
                / func.nullif(total_ingresos_subq, 0),
                1,
            ).label("porcentaje"),
        )
        .join(PeliculaGenero, Genero.id_genero == PeliculaGenero.id_genero)
        .join(Pelicula, Pelicula.id_pelicula == PeliculaGenero.id_pelicula)
        .join(Funcion, and_(*funcion_cond))
        .join(Transaccion, and_(*transaccion_cond))
        .filter(Transaccion.estado_pago == "Aprobado")
        .group_by(Genero.id_genero, Genero.nombre_genero)
        .order_by(func.coalesce(func.sum(Transaccion.monto_total), 0).desc())
        .all()
    )

    data = [
        {
            "id_genero": r.id_genero,
            "genero": r.genero,
            "peliculas": r.peliculas,
            "funciones": r.funciones,
            "ingresos": float(r.ingresos),
            "porcentaje": float(r.porcentaje) if r.porcentaje is not None else 0.0,
        }
        for r in rows
    ]

    ingreso_total = sum(r["ingresos"] for r in data)
    total_peliculas = sum(r["peliculas"] for r in data)
    genero_principal = data[0]["genero"] if data else ""

    return {
        "data": data,
        "resumen": {
            "genero_principal": genero_principal,
            "ingreso_total": round(ingreso_total, 2),
            "total_peliculas": total_peliculas,
        },
    }


def get_detalle_compras_data(db: Session, periodo: str):
    hoy = datetime.now()
    inicio, fin = _get_periodo_fechas(periodo, hoy)

    query = (
        db.query(
            Transaccion.id_transaccion,
            Usuario.nombre.label("cliente"),
            Pelicula.titulo.label("pelicula"),
            Sala.nombre_sala.label("sala"),
            func.count(func.distinct(DetalleBoletaAsiento.id_detalle_asiento)).label("boletos"),
            func.coalesce(func.sum(Transaccion.monto_total), 0).label("total"),
            Transaccion.fecha_transaccion.label("fecha"),
            Transaccion.estado_pago.label("estado"),
        )
        .join(Usuario, Usuario.id_usuario == Transaccion.id_usuario)
        .join(Funcion, Funcion.id_funcion == Transaccion.id_funcion)
        .join(Pelicula, Pelicula.id_pelicula == Funcion.id_pelicula)
        .join(Sala, Sala.id_sala == Funcion.id_sala)
        .outerjoin(DetalleBoletaAsiento, DetalleBoletaAsiento.id_transaccion == Transaccion.id_transaccion)
        .filter(Transaccion.estado_pago == "Aprobado")
    )
    query = _filter_fecha_range(query, Transaccion.fecha_transaccion, inicio, fin)
    rows = query.group_by(Transaccion.id_transaccion, Usuario.nombre, Pelicula.titulo,
                          Sala.nombre_sala, Transaccion.fecha_transaccion, Transaccion.estado_pago
                  ).order_by(Transaccion.fecha_transaccion.desc()).all()

    data = []
    total_boletos = 0
    total_snacks = 0
    for r in rows:
        snacks = (
            db.query(
                func.concat(ProductoConfiteria.nombre_producto, " x", DetalleBoletaConfiteria.cantidad)
            )
            .join(ProductoConfiteria, ProductoConfiteria.id_producto == DetalleBoletaConfiteria.id_producto)
            .filter(DetalleBoletaConfiteria.id_transaccion == r.id_transaccion)
            .all()
        )
        snacks_str = ", ".join(s[0] for s in snacks) if snacks else ""
        items_count = (
            db.query(func.sum(DetalleBoletaConfiteria.cantidad))
            .filter(DetalleBoletaConfiteria.id_transaccion == r.id_transaccion)
            .scalar() or 0
        )
        total_boletos += r.boletos
        total_snacks += items_count
        data.append({
            "id_transaccion": r.id_transaccion,
            "cliente": r.cliente,
            "pelicula": r.pelicula,
            "sala": r.sala,
            "boletos": r.boletos,
            "confiteria": snacks_str,
            "total": float(r.total),
            "fecha": r.fecha.isoformat() if r.fecha else None,
            "estado": r.estado,
        })

    return {
        "data": data,
        "resumen": {
            "total_transacciones": len(data),
            "total_ingresos": round(sum(d["total"] for d in data), 2),
            "total_boletos": total_boletos,
            "total_snacks": total_snacks,
        },
    }


def get_reporte_contador(db: Session):
    row = db.query(ReporteContador).filter(ReporteContador.id == 1).first()
    if not row:
        row = ReporteContador(id=1, count=0, ultima_generacion=None)
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


def incrementar_reporte_contador(db: Session):
    from datetime import datetime
    row = get_reporte_contador(db)
    row.count += 1
    row.ultima_generacion = datetime.now()
    db.commit()
    db.refresh(row)
    return {"count": row.count, "ultima_generacion": row.ultima_generacion.isoformat() if row.ultima_generacion else None}

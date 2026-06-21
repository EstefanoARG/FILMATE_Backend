from datetime import datetime, timedelta

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.movie import Pelicula
from app.models.room import Sala
from app.models.showtime import Funcion
from app.models.showtime_seat import AsientoFuncion
from app.models.transaccion import Transaccion
from app.models.user import Usuario


def get_ventas_por_dia(db: Session, inicio: datetime, fin: datetime):
    resultados = (
        db.query(
            func.date(Transaccion.fecha_transaccion).label("dia"),
            func.count(Transaccion.id_transaccion).label("ventas"),
        )
        .filter(
            Transaccion.estado_pago == "Aprobado",
            Transaccion.fecha_transaccion.between(inicio, fin),
        )
        .group_by(func.date(Transaccion.fecha_transaccion))
        .order_by(func.date(Transaccion.fecha_transaccion))
        .all()
    )
    ventas_dict = {row.dia.strftime("%Y-%m-%d"): row.ventas for row in resultados}
    resultado_final = []
    delta = fin - inicio
    for i in range(delta.days + 1):
        dia = (inicio + timedelta(days=i)).strftime("%Y-%m-%d")
        resultado_final.append({"dia": dia, "ventas": ventas_dict.get(dia, 0)})
    return resultado_final


def get_pelicula_mas_taquillera(db: Session, inicio: datetime):
    resultado = (
        db.query(
            Pelicula.titulo,
            func.coalesce(func.sum(Transaccion.monto_total), 0).label("total"),
        )
        .join(Funcion, Funcion.id_funcion == Transaccion.id_funcion)
        .join(Pelicula, Pelicula.id_pelicula == Funcion.id_pelicula)
        .filter(
            Transaccion.estado_pago == "Aprobado",
            Transaccion.fecha_transaccion >= inicio,
        )
        .group_by(Pelicula.id_pelicula, Pelicula.titulo)
        .order_by(func.coalesce(func.sum(Transaccion.monto_total), 0).desc())
        .first()
    )
    if resultado:
        return {"titulo": resultado.titulo, "total": float(resultado.total)}
    return None


def get_ocupacion_promedio(db: Session, inicio: datetime, fin: datetime):
    resultado = (
        db.query(
            func.count(case((AsientoFuncion.estado == "Ocupado", 1))) * 100.0
            / func.count(AsientoFuncion.id_asiento)
        )
        .join(Funcion, AsientoFuncion.id_funcion == Funcion.id_funcion)
        .filter(Funcion.fecha_hora.between(inicio, fin))
        .scalar()
    )
    return round(float(resultado), 2) if resultado else 0.0


def get_ingresos_por_formato(db: Session, inicio: datetime, fin: datetime):
    resultados = (
        db.query(
            Sala.tipo_formato,
            func.coalesce(func.sum(Transaccion.monto_total), 0).label("total"),
        )
        .join(Funcion, Funcion.id_funcion == Transaccion.id_funcion)
        .join(Sala, Sala.id_sala == Funcion.id_sala)
        .filter(
            Transaccion.estado_pago == "Aprobado",
            Transaccion.fecha_transaccion.between(inicio, fin),
        )
        .group_by(Sala.tipo_formato)
        .all()
    )
    return [{"tipo_formato": row.tipo_formato, "total": float(row.total)} for row in resultados]


def get_ingresos_por_categoria(db: Session, inicio: datetime, fin: datetime):
    resultados = (
        db.query(
            Sala.tipo_sala,
            func.coalesce(func.sum(Transaccion.monto_total), 0).label("total"),
        )
        .join(Funcion, Funcion.id_funcion == Transaccion.id_funcion)
        .join(Sala, Sala.id_sala == Funcion.id_sala)
        .filter(
            Transaccion.estado_pago == "Aprobado",
            Transaccion.fecha_transaccion.between(inicio, fin),
        )
        .group_by(Sala.tipo_sala)
        .all()
    )
    return [{"tipo_sala": row.tipo_sala, "total": float(row.total)} for row in resultados]


def get_nuevos_usuarios(db: Session, desde: datetime):
    return (
        db.query(func.count(Usuario.id_usuario))
        .filter(Usuario.fecha_registro >= desde)
        .scalar()
    ) or 0


def _get_metricas_periodo(db: Session, desde: datetime, hasta: datetime):
    ventas = (
        db.query(func.count(Transaccion.id_transaccion))
        .filter(
            Transaccion.estado_pago == "Aprobado",
            Transaccion.fecha_transaccion >= desde,
            Transaccion.fecha_transaccion < hasta,
        )
        .scalar()
    ) or 0

    ingresos = (
        db.query(func.coalesce(func.sum(Transaccion.monto_total), 0))
        .filter(
            Transaccion.estado_pago == "Aprobado",
            Transaccion.fecha_transaccion >= desde,
            Transaccion.fecha_transaccion < hasta,
        )
        .scalar()
    ) or 0

    usuarios = (
        db.query(func.count(Usuario.id_usuario))
        .filter(
            Usuario.fecha_registro >= desde,
            Usuario.fecha_registro < hasta,
        )
        .scalar()
    ) or 0

    return {
        "ventas": ventas,
        "ingresos": float(ingresos),
        "nuevosUsuarios": usuarios,
    }


def _calcular_cambio(actual, anterior):
    if anterior and anterior != 0:
        return round((actual - anterior) / anterior * 100, 2)
    return 0.0 if actual == 0 else 100.0


def _calcular_periodo(periodo: str, hoy: datetime):
    if periodo == "hoy":
        inicio = hoy.replace(hour=0, minute=0, second=0, microsecond=0)
        fin = hoy
    elif periodo == "semana":
        inicio = (hoy - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        fin = hoy
    elif periodo == "mes_anterior":
        inicio = (hoy.replace(day=1) - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fin = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        inicio = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fin = hoy
    return inicio, fin


def get_dashboard_data(db: Session, periodo: str = "mes"):
    hoy = datetime.now()
    inicio, fin = _calcular_periodo(periodo, hoy)

    duracion = fin - inicio
    inicio_anterior = inicio - duracion
    fin_anterior = inicio

    actual = _get_metricas_periodo(db, inicio, fin)
    anterior = _get_metricas_periodo(db, inicio_anterior, fin_anterior)

    return {
        "ventasPorDia": get_ventas_por_dia(db, inicio, fin),
        "peliculaMasTaquillera": get_pelicula_mas_taquillera(db, inicio),
        "ocupacionPromedio": get_ocupacion_promedio(db, inicio, fin),
        "ingresosPorFormato": get_ingresos_por_formato(db, inicio, fin),
        "ingresosPorCategoria": get_ingresos_por_categoria(db, inicio, fin),
        "nuevosUsuarios": get_nuevos_usuarios(db, inicio),
        "comparacion": {
            "ventas": {
                "actual": actual["ventas"],
                "anterior": anterior["ventas"],
                "cambioPorcentual": _calcular_cambio(actual["ventas"], anterior["ventas"]),
            },
            "ingresos": {
                "actual": actual["ingresos"],
                "anterior": anterior["ingresos"],
                "cambioPorcentual": _calcular_cambio(actual["ingresos"], anterior["ingresos"]),
            },
            "nuevosUsuarios": {
                "actual": actual["nuevosUsuarios"],
                "anterior": anterior["nuevosUsuarios"],
                "cambioPorcentual": _calcular_cambio(actual["nuevosUsuarios"], anterior["nuevosUsuarios"]),
            },
        },
    }

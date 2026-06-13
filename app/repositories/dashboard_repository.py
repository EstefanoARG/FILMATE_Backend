from datetime import datetime, timedelta

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.movie import Pelicula
from app.models.room import Sala
from app.models.showtime import Funcion
from app.models.showtime_seat import AsientoFuncion
from app.models.transaccion import Transaccion
from app.models.user import Usuario


def get_ventas_por_dia(db: Session):
    inicio = datetime.now() - timedelta(days=7)
    resultados = (
        db.query(
            func.date(Transaccion.fecha_transaccion).label("dia"),
            func.count(Transaccion.id_transaccion).label("ventas"),
        )
        .filter(
            Transaccion.estado_pago == "Aprobado",
            Transaccion.fecha_transaccion >= inicio,
        )
        .group_by(func.date(Transaccion.fecha_transaccion))
        .order_by(func.date(Transaccion.fecha_transaccion))
        .all()
    )
    return [{"dia": row.dia, "ventas": row.ventas} for row in resultados]


def get_pelicula_mas_taquillera(db: Session):
    resultado = (
        db.query(
            Pelicula.titulo,
            func.coalesce(func.sum(Transaccion.monto_total), 0).label("total"),
        )
        .join(Funcion, Funcion.id_funcion == Transaccion.id_funcion)
        .join(Pelicula, Pelicula.id_pelicula == Funcion.id_pelicula)
        .filter(Transaccion.estado_pago == "Aprobado")
        .group_by(Pelicula.id_pelicula, Pelicula.titulo)
        .order_by(func.coalesce(func.sum(Transaccion.monto_total), 0).desc())
        .first()
    )
    if resultado:
        return {"titulo": resultado.titulo, "total": float(resultado.total)}
    return None


def get_ocupacion_promedio(db: Session):
    resultado = (
        db.query(
            func.count(case((AsientoFuncion.estado == "Ocupado", 1))) * 100.0
            / func.count(AsientoFuncion.id_asiento)
        )
        .join(Funcion, AsientoFuncion.id_funcion == Funcion.id_funcion)
        .filter(Funcion.fecha_hora >= datetime.now())
        .scalar()
    )
    return round(float(resultado), 2) if resultado else 0.0


def get_ingresos_por_formato(db: Session):
    resultados = (
        db.query(
            Sala.tipo_formato,
            func.coalesce(func.sum(Transaccion.monto_total), 0).label("total"),
        )
        .join(Funcion, Funcion.id_funcion == Transaccion.id_funcion)
        .join(Sala, Sala.id_sala == Funcion.id_sala)
        .filter(Transaccion.estado_pago == "Aprobado")
        .group_by(Sala.tipo_formato)
        .all()
    )
    return [{"tipo_formato": row.tipo_formato, "total": float(row.total)} for row in resultados]


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


def get_dashboard_data(db: Session):
    today = datetime.now()
    inicio_mes_actual = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    fin_mes_anterior = inicio_mes_actual - timedelta(days=1)
    inicio_mes_anterior = fin_mes_anterior.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    actual = _get_metricas_periodo(db, inicio_mes_actual, today)
    anterior = _get_metricas_periodo(db, inicio_mes_anterior, inicio_mes_actual)

    return {
        "ventasPorDia": get_ventas_por_dia(db),
        "peliculaMasTaquillera": get_pelicula_mas_taquillera(db),
        "ocupacionPromedio": get_ocupacion_promedio(db),
        "ingresosPorFormato": get_ingresos_por_formato(db),
        "nuevosUsuarios": get_nuevos_usuarios(db, inicio_mes_actual),
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

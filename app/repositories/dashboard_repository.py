from datetime import datetime, timedelta

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.movie import Pelicula
from app.models.cinema import Cine
from app.models.room import Sala
from app.models.showtime import Funcion
from app.models.showtime_seat import AsientoFuncion
from app.models.transaccion import Transaccion
from app.models.user import Usuario
from app.models.detalle_boleta_asiento import DetalleBoletaAsiento
from app.models.detalle_boleta_confiteria import DetalleBoletaConfiteria


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


def get_pelicula_mas_taquillera(db: Session, inicio: datetime, fin: datetime):
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
            Transaccion.fecha_transaccion < fin,
        )
        .group_by(Pelicula.id_pelicula, Pelicula.titulo)
        .order_by(func.coalesce(func.sum(Transaccion.monto_total), 0).desc())
        .first()
    )
    if resultado:
        return {"titulo": resultado.titulo, "total": float(resultado.total)}
    return None


def get_salas_dashboard(db: Session):
    rows = (
        db.query(Sala, Cine.nombre_cine)
        .outerjoin(Cine, Cine.id_cine == Sala.id_cine)
        .filter(Sala.eliminado == False)
        .order_by(Sala.id_cine, Sala.id_sala)
        .all()
    )
    return [
        {
            "id_sala": sala.id_sala,
            "id_cine": sala.id_cine,
            "nombre_sala": sala.nombre_sala,
            "tipo_sala": sala.tipo_sala,
            "capacidad_asientos": sala.capacidad_asientos,
            "nombre_cine": nombre_cine,
        }
        for sala, nombre_cine in rows
    ]


def get_ultimas_transacciones(db: Session, inicio: datetime, fin: datetime, limit: int = 40):
    boletos_subq = (
        db.query(
            DetalleBoletaAsiento.id_transaccion.label("id_transaccion"),
            func.count(DetalleBoletaAsiento.id_detalle_asiento).label("boletos"),
        )
        .group_by(DetalleBoletaAsiento.id_transaccion)
        .subquery()
    )
    snacks_subq = (
        db.query(
            DetalleBoletaConfiteria.id_transaccion.label("id_transaccion"),
            func.count(DetalleBoletaConfiteria.id_detalle_confi).label("snacks"),
        )
        .group_by(DetalleBoletaConfiteria.id_transaccion)
        .subquery()
    )

    rows = (
        db.query(
            Transaccion,
            Usuario.nombre.label("cliente"),
            Pelicula.titulo.label("pelicula"),
            Sala.nombre_sala.label("sala"),
            func.coalesce(boletos_subq.c.boletos, 0).label("boletos"),
            func.coalesce(snacks_subq.c.snacks, 0).label("snacks"),
        )
        .outerjoin(Usuario, Usuario.id_usuario == Transaccion.id_usuario)
        .outerjoin(Funcion, Funcion.id_funcion == Transaccion.id_funcion)
        .outerjoin(Pelicula, Pelicula.id_pelicula == Funcion.id_pelicula)
        .outerjoin(Sala, Sala.id_sala == Funcion.id_sala)
        .outerjoin(boletos_subq, boletos_subq.c.id_transaccion == Transaccion.id_transaccion)
        .outerjoin(snacks_subq, snacks_subq.c.id_transaccion == Transaccion.id_transaccion)
        .filter(
            Transaccion.fecha_transaccion >= inicio,
            Transaccion.fecha_transaccion < fin,
        )
        .order_by(Transaccion.fecha_transaccion.desc())
        .limit(limit)
        .all()
    )

    transactions = []
    for txn, cliente, pelicula, sala, boletos, snacks in rows:
        if boletos and snacks:
            tipo = "Entrada + Dulcería"
        elif snacks:
            tipo = "Solo Dulcería"
        else:
            tipo = "Solo Entrada"

        transactions.append({
            "id_transaccion": txn.id_transaccion,
            "cliente": cliente or "Cliente",
            "pelicula": pelicula or "Dulcería",
            "sala": sala or "Sin sala",
            "monto_total": float(txn.monto_total),
            "estado_pago": txn.estado_pago,
            "metodo_pago": txn.metodo_pago,
            "fecha_transaccion": txn.fecha_transaccion,
            "tipo": tipo,
        })

    return transactions


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
        "peliculaMasTaquillera": get_pelicula_mas_taquillera(db, inicio, fin),
        "ocupacionPromedio": get_ocupacion_promedio(db, inicio, fin),
        "ingresosPorFormato": get_ingresos_por_formato(db, inicio, fin),
        "ingresosPorCategoria": get_ingresos_por_categoria(db, inicio, fin),
        "nuevosUsuarios": get_nuevos_usuarios(db, inicio),
        "ventasMes": actual["ventas"],
        "ultimasTransacciones": get_ultimas_transacciones(db, inicio, fin),
        "salas": get_salas_dashboard(db),
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

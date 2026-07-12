from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.models.solicitud_reembolso import SolicitudReembolso
from app.models.transaccion import Transaccion
from app.models.user import Usuario


def create_solicitud(
    db: Session,
    id_transaccion: int,
    motivo: str,
    monto_reembolsado: float,
    tipo_reembolso: str,
) -> SolicitudReembolso:
    solicitud = SolicitudReembolso(
        id_transaccion=id_transaccion,
        motivo=motivo,
        monto_reembolsado=monto_reembolsado,
        tipo_reembolso=tipo_reembolso,
    )
    db.add(solicitud)
    return solicitud


def list_solicitudes_by_user(db: Session, id_usuario: int) -> List[SolicitudReembolso]:
    return (
        db.query(SolicitudReembolso)
        .join(Transaccion, Transaccion.id_transaccion == SolicitudReembolso.id_transaccion)
        .filter(Transaccion.id_usuario == id_usuario)
        .order_by(SolicitudReembolso.fecha_solicitud.desc())
        .all()
    )


def list_solicitudes_admin(
    db: Session,
    estado: Optional[str] = None,
    tipo_reembolso: Optional[str] = None,
    fecha: Optional[str] = None,
    buscar: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> List[SolicitudReembolso]:
    query = db.query(SolicitudReembolso).join(Transaccion, Transaccion.id_transaccion == SolicitudReembolso.id_transaccion)

    if estado:
        query = query.filter(SolicitudReembolso.estado_solicitud == estado)

    if tipo_reembolso:
        query = query.filter(SolicitudReembolso.tipo_reembolso == tipo_reembolso)

    if fecha:
        dias_map = {"1d": 1, "7d": 7, "30d": 30}
        dias = dias_map.get(fecha)
        if dias:
            query = query.filter(SolicitudReembolso.fecha_solicitud >= datetime.now() - timedelta(days=dias))

    if buscar:
        query = query.join(Usuario, Usuario.id_usuario == Transaccion.id_usuario)
        buscar_filters = [
            Usuario.nombre.ilike(f"%{buscar}%"),
            Usuario.documento.ilike(f"%{buscar}%"),
            SolicitudReembolso.motivo.ilike(f"%{buscar}%"),
        ]
        try:
            buscar_id = int(buscar)
            buscar_filters.append(SolicitudReembolso.id_reembolso == buscar_id)
            buscar_filters.append(SolicitudReembolso.id_transaccion == buscar_id)
        except ValueError:
            pass
        query = query.filter(or_(*buscar_filters))

    return query.order_by(SolicitudReembolso.fecha_solicitud.desc()).offset(skip).limit(limit).all()


def get_solicitud(db: Session, solicitud_id: int) -> Optional[SolicitudReembolso]:
    return db.query(SolicitudReembolso).filter(SolicitudReembolso.id_reembolso == solicitud_id).first()


def resolve_solicitud(
    db: Session,
    solicitud_id: int,
    estado_solicitud: str,
    comentario_administrador: Optional[str] = None,
) -> Optional[SolicitudReembolso]:
    solicitud = get_solicitud(db, solicitud_id)
    if not solicitud:
        return None
    solicitud.estado_solicitud = estado_solicitud
    solicitud.fecha_resolucion = datetime.now()
    if comentario_administrador is not None:
        solicitud.comentario_administrador = comentario_administrador
    if estado_solicitud == "Aprobada":
        txn = db.query(Transaccion).filter(Transaccion.id_transaccion == solicitud.id_transaccion).first()
        if txn:
            txn.estado_pago = "Reembolsada"
    db.commit()
    db.refresh(solicitud)
    return solicitud


def count_solicitudes_by_estado(db: Session) -> dict:
    counts = (
        db.query(
            SolicitudReembolso.estado_solicitud,
            func.count(SolicitudReembolso.id_reembolso),
        )
        .group_by(SolicitudReembolso.estado_solicitud)
        .all()
    )
    total_monto = float(
        db.query(func.coalesce(func.sum(SolicitudReembolso.monto_reembolsado), 0))
        .filter(SolicitudReembolso.estado_solicitud == "Aprobada")
        .scalar()
    )
    result = {"pendientes": 0, "aprobadas": 0, "rechazadas": 0, "evaluacion": 0, "monto_total_aprobado": total_monto}
    for estado, count in counts:
        key = estado.lower() + ("s" if not estado.lower().endswith("s") else "")
        if key in result:
            result[key] = count
    return result

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.bloqueo_temporal import BloqueoTemporal
from app.models.showtime_seat import AsientoFuncion
from typing import List


def bloquear_asientos(db: Session, user_id: int, funcion_id: int, asiento_ids: List[int], minutos: int = 10) -> List[BloqueoTemporal]:
    expira = datetime.now() + timedelta(minutes=minutos)
    creados = []
    for aid in asiento_ids:
        bt = BloqueoTemporal(id_usuario=user_id, id_funcion=funcion_id, id_asiento=aid, expira_en=expira)
        db.add(bt)
        creados.append(bt)

        af = (
            db.query(AsientoFuncion)
            .filter(AsientoFuncion.id_funcion == funcion_id, AsientoFuncion.id_asiento == aid)
            .first()
        )
        if af and af.estado == "Disponible":
            af.estado = "Bloqueado"

    db.commit()
    for bt in creados:
        db.refresh(bt)
    return creados


def limpiar_bloqueos_expirados(db: Session):
    expirados = db.query(BloqueoTemporal).filter(BloqueoTemporal.expira_en < datetime.now()).all()
    for bt in expirados:
        af = (
            db.query(AsientoFuncion)
            .filter(AsientoFuncion.id_funcion == bt.id_funcion, AsientoFuncion.id_asiento == bt.id_asiento)
            .first()
        )
        if af and af.estado == "Bloqueado":
            af.estado = "Disponible"
        db.delete(bt)
    db.commit()

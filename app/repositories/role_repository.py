from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.permiso import Permiso
from app.models.role import Rol
from app.models.rol_permiso import RolPermiso


def list_roles(db: Session) -> List[Rol]:
    return db.query(Rol).all()


def get_role_by_id(db: Session, role_id: int) -> Optional[Rol]:
    return db.query(Rol).filter(Rol.id_role == role_id).first()


def create_role(db: Session, nombre_rol: str, descripcion: Optional[str] = None) -> Rol:
    rol = Rol(nombre_rol=nombre_rol, descripcion=descripcion)
    db.add(rol)
    db.commit()
    db.refresh(rol)
    return rol


def update_role(db: Session, role_id: int, data: dict) -> Optional[Rol]:
    rol = get_role_by_id(db, role_id)
    if not rol:
        return None
    for key, value in data.items():
        if hasattr(rol, key) and value is not None:
            setattr(rol, key, value)
    db.commit()
    db.refresh(rol)
    return rol


def delete_role(db: Session, role_id: int) -> bool:
    rol = get_role_by_id(db, role_id)
    if not rol:
        return False
    db.delete(rol)
    db.commit()
    return True


def get_role_permisos(db: Session, role_id: int) -> List[Permiso]:
    return (
        db.query(Permiso)
        .join(RolPermiso, RolPermiso.id_permiso == Permiso.id_permiso)
        .filter(RolPermiso.id_role == role_id)
        .all()
    )


def assign_permisos_to_role(db: Session, role_id: int, permiso_ids: List[int]):
    db.query(RolPermiso).filter(RolPermiso.id_role == role_id).delete()
    for pid in permiso_ids:
        db.add(RolPermiso(id_role=role_id, id_permiso=pid))
    db.commit()


def get_role_with_permisos(db: Session, role_id: int) -> Optional[dict]:
    from app.schemas.permiso import PermisoResponse

    rol = get_role_by_id(db, role_id)
    if not rol:
        return None
    permisos = get_role_permisos(db, role_id)
    return {
        "id_role": rol.id_role,
        "nombre_rol": rol.nombre_rol,
        "descripcion": rol.descripcion,
        "permisos": [PermisoResponse.model_validate(p) for p in permisos],
    }

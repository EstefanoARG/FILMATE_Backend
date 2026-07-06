from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.permiso import Permiso


def list_permisos(db: Session) -> List[Permiso]:
    return db.query(Permiso).order_by(Permiso.modulo, Permiso.codigo_permiso).all()


def get_permiso_by_id(db: Session, permiso_id: int) -> Optional[Permiso]:
    return db.query(Permiso).filter(Permiso.id_permiso == permiso_id).first()


def create_permiso(db: Session, codigo_permiso: str, descripcion: str, modulo: str) -> Permiso:
    permiso = Permiso(
        codigo_permiso=codigo_permiso,
        descripcion=descripcion,
        modulo=modulo,
    )
    db.add(permiso)
    db.commit()
    db.refresh(permiso)
    return permiso


def delete_permiso(db: Session, permiso_id: int) -> bool:
    permiso = get_permiso_by_id(db, permiso_id)
    if not permiso:
        return False
    db.delete(permiso)
    db.commit()
    return True


def user_has_permission(db: Session, user_id: int, codigo_permiso: str) -> bool:
    from app.models.permiso import Permiso
    from app.models.rol_permiso import RolPermiso
    from app.models.usuario_rol import UsuarioRol

    subquery = (
        db.query(Permiso.id_permiso)
        .filter(Permiso.codigo_permiso == codigo_permiso)
        .scalar_subquery()
    )
    count = (
        db.query(UsuarioRol)
        .join(RolPermiso, RolPermiso.id_role == UsuarioRol.id_role)
        .filter(
            UsuarioRol.id_usuario == user_id,
            RolPermiso.id_permiso == subquery,
        )
        .count()
    )
    return count > 0

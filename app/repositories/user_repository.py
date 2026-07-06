from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import Usuario
from app.models.usuario_rol import UsuarioRol


def get_user_by_id(db: Session, user_id: int) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.id_usuario == user_id, Usuario.eliminado == False).first()


def get_user_by_email(db: Session, email: str) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.correo == email, Usuario.eliminado == False).first()


def get_user_by_username(db: Session, username: str) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.username == username, Usuario.eliminado == False).first()


def list_users(db: Session, estado: Optional[str] = None) -> List[Usuario]:
    query = db.query(Usuario).filter(Usuario.eliminado == False)
    if estado:
        query = query.filter(Usuario.estado_usuario == estado)
    return query.order_by(Usuario.id_usuario).all()


def create_user(db: Session, user: Usuario) -> Usuario:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, data: dict) -> Optional[Usuario]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    for key, value in data.items():
        if hasattr(user, key) and value is not None:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def assign_role(db: Session, user_id: int, role_id: int) -> UsuarioRol:
    ur = UsuarioRol(id_usuario=user_id, id_role=role_id)
    db.add(ur)
    db.commit()
    return ur


def get_user_roles(db: Session, user_id: int) -> List[int]:
    rows = db.query(UsuarioRol.id_role).filter(UsuarioRol.id_usuario == user_id).all()
    return [r.id_role for r in rows]


def soft_delete_user(db: Session, user_id: int) -> Optional[Usuario]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.eliminado = True
    user.fecha_eliminacion = datetime.now()
    user.estado_usuario = "INACTIVO"
    db.commit()
    db.refresh(user)
    return user


def remove_role(db: Session, user_id: int, role_id: int) -> bool:
    deleted = db.query(UsuarioRol).filter(
        UsuarioRol.id_usuario == user_id,
        UsuarioRol.id_role == role_id
    ).delete()
    db.commit()
    return deleted > 0


def set_user_roles(db: Session, user_id: int, role_ids: List[int]):
    db.query(UsuarioRol).filter(UsuarioRol.id_usuario == user_id).delete()
    for rid in role_ids:
        db.add(UsuarioRol(id_usuario=user_id, id_role=rid))
    db.commit()


def search_users_by_text(db: Session, text: str, limit: int = 20) -> List[Usuario]:
    if not text:
        return []

    pattern = f"%{text}%"
    query = (
        db.query(Usuario)
        .filter(Usuario.eliminado == False)
        .filter(Usuario.estado_usuario == 'ACTIVO')
        .filter(
            or_(
                Usuario.username.ilike(pattern),
                Usuario.nombre.ilike(pattern),
                Usuario.correo.ilike(pattern),
            )
        )
        .order_by(Usuario.id_usuario)
        .limit(limit)
    )

    return query.all()

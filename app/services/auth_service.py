from sqlalchemy.orm import Session

from app.core import security
from app.models.user import Usuario
from app.repositories import user_repository
from app.schemas.user import UserCreate, UserLogin


def register_user(db: Session, payload: UserCreate, default_role_id: int = 2) -> Usuario:
    existing_email = user_repository.get_user_by_email(db, payload.correo)
    if existing_email:
        raise ValueError("Email already registered")

    existing_username = user_repository.get_user_by_username(db, payload.username)
    if existing_username:
        raise ValueError("Username already taken")

    hashed_password = security.hash_password(payload.contrasena)
    user = Usuario(
        nombre=payload.nombre,
        username=payload.username,
        correo=payload.correo,
        contrasena=hashed_password,
        id_tipo_doc=payload.id_tipo_doc,
        numero_documento=payload.numero_documento,
        telefono=payload.telefono,
        url_perfil=payload.url_perfil,
    )

    user = user_repository.create_user(db, user)
    user_repository.assign_role(db, user.id_usuario, default_role_id)
    return user


def authenticate_user(db: Session, payload: UserLogin) -> Usuario:
    user = user_repository.get_user_by_email(db, payload.correo)
    if not user:
        raise ValueError("Invalid credentials")

    if not security.verify_password(payload.contrasena, user.contrasena):
        raise ValueError("Invalid credentials")

    if user.estado_usuario != "ACTIVO":
        raise ValueError("User account is not active")

    return user

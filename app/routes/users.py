import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import Query
from app.core.dependencies import get_db
from app.repositories import user_repository
from app.schemas.user import UserResponse, UserUpdate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/search")
def search_users(q: Annotated[str, Query()], db: Annotated[Session, Depends(get_db)]):
    """Buscador global de usuarios por nombre o username."""
    from app.models.user import Usuario

    usuarios = db.query(Usuario).filter(
        or_(
            Usuario.username.ilike(f"%{q}%"),
            Usuario.nombre.ilike(f"%{q}%")
        ),
        Usuario.eliminado == False
    ).limit(20).all()

    return [
        {
            "id_usuario": u.id_usuario,
            "username": u.username,
            "nombre": u.nombre,
            "url_perfil": u.url_perfil
        }
        for u in usuarios
    ]


@router.get("/{user_id}", response_model=UserResponse, responses={404: {"description": "User not found"}})
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = user_repository.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    r = UserResponse.model_validate(user)
    r.roles = user_repository.get_user_roles(db, user.id_usuario)
    return r


@router.put("/{user_id}", response_model=UserResponse, responses={404: {"description": "User not found"}})
def update_user(user_id: int, payload: UserUpdate, db: Annotated[Session, Depends(get_db)]):
    data = payload.model_dump(exclude_unset=True)
    user = user_repository.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    r = UserResponse.model_validate(user)
    r.roles = user_repository.get_user_roles(db, user.id_usuario)
    return r
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.repositories import user_repository
from app.schemas.user import UserCreate, UserResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/users", tags=["admin users"])


@router.get("/", response_model=List[UserResponse])
def admin_list_users(estado: Optional[str] = None, db: Session = Depends(get_db)):
    users = user_repository.list_users(db, estado)
    result = []
    for u in users:
        r = UserResponse.model_validate(u)
        r.roles = user_repository.get_user_roles(db, u.id_usuario)
        result.append(r)
    return result


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    from app.services.auth_service import register_user
    try:
        user = register_user(db, payload)
        roles = user_repository.get_user_roles(db, user.id_usuario)
        resp = UserResponse.model_validate(user)
        resp.roles = roles
        return resp
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

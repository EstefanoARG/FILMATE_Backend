import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.auth import LoginResponse
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth_service import authenticate_user, register_user
from app.repositories.user_repository import get_user_roles

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, responses={400: {"description": "Bad request"}, 500: {"description": "Internal server error"}})
def register(payload: UserCreate, db: Annotated[Session, Depends(get_db)]):
    logger.info("POST /auth/register - correo=%s", payload.correo)
    try:
        user = register_user(db, payload)
        roles = get_user_roles(db, user.id_usuario)
        resp = UserResponse.model_validate(user)
        resp.roles = roles
        return resp
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Error en POST /auth/register")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/login", response_model=LoginResponse, responses={401: {"description": "Unauthorized"}, 500: {"description": "Internal server error"}})
def login(payload: UserLogin, db: Annotated[Session, Depends(get_db)]):
    logger.info("POST /auth/login - correo=%s", payload.correo)
    try:
        user = authenticate_user(db, payload)
        roles = get_user_roles(db, user.id_usuario)
        resp = UserResponse.model_validate(user)
        resp.roles = roles
        return LoginResponse(message="Login successful", user=resp)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    except Exception as exc:
        logger.exception("Error en POST /auth/login")
        raise HTTPException(status_code=500, detail=str(exc))

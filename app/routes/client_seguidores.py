import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.repositories import seguidor_repository
from app.schemas.seguidor import SeguirRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/client/seguidores", tags=["client seguidores"])

@router.post("/seguir")
def follow(payload: SeguirRequest, db: Annotated[Session, Depends(get_db)]):
    seguidor_repository.follow(db, payload.id_usuario, payload.id_seguir)
    return {"message": "Ahora sigues a este usuario"}

@router.post("/dejar-de-seguir")
def unfollow(payload: SeguirRequest, db: Annotated[Session, Depends(get_db)]):
    seguidor_repository.unfollow(db, payload.id_usuario, payload.id_seguir)
    return {"message": "Dejaste de seguir a este usuario"}
@router.get("/check/{seguidor_id}/sigue-a/{seguido_id}")
def check_follow(seguidor_id: int, seguido_id: int, db: Annotated[Session, Depends(get_db)]):
    siguiendo = seguidor_repository.is_following(db, seguidor_id, seguido_id)
    return {"siguiendo": siguiendo}


@router.get("/{user_id}/counts")
def get_follow_counts(user_id: int, db: Annotated[Session, Depends(get_db)]):
    return {
        "seguidores": seguidor_repository.count_followers(db, user_id),
        "siguiendo": seguidor_repository.count_following(db, user_id),
    }


@router.get("/{user_id}/seguidores")
def list_followers(user_id: int, db: Annotated[Session, Depends(get_db)]):
    return seguidor_repository.list_followers(db, user_id)


@router.get("/{user_id}/siguiendo")
def list_following(user_id: int, db: Annotated[Session, Depends(get_db)]):
    return seguidor_repository.list_following(db, user_id)
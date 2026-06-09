import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.repositories import seguidor_repository
from app.schemas.seguidor import SeguirRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/client/seguidores", tags=["client seguidores"])

@router.post("/seguir")
def follow(payload: SeguirRequest, db: Session = Depends(get_db)):
    seguidor_repository.follow(db, payload.id_usuario, payload.id_seguir)
    return {"message": "Ahora sigues a este usuario"}

@router.post("/dejar-de-seguir")
def unfollow(payload: SeguirRequest, db: Session = Depends(get_db)):
    seguidor_repository.unfollow(db, payload.id_usuario, payload.id_seguir)
    return {"message": "Dejaste de seguir a este usuario"}

@router.get("/{user_id}/seguidores")
def list_followers(user_id: int, db: Session = Depends(get_db)):
    return seguidor_repository.list_followers(db, user_id)

@router.get("/{user_id}/siguiendo")
def list_following(user_id: int, db: Session = Depends(get_db)):
    return seguidor_repository.list_following(db, user_id)
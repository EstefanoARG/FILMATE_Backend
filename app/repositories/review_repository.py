from sqlalchemy.orm import Session
from app.models.review import Resena
from typing import List, Optional


def get_review(db: Session, review_id: int) -> Optional[Resena]:
    return db.query(Resena).filter(Resena.id_resena == review_id).first()


def list_reviews_for_movie(db: Session, movie_id: int) -> List[Resena]:
    return db.query(Resena).filter(Resena.id_pelicula == movie_id).all()


def create_review(db: Session, review: Resena) -> Resena:
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def delete_review(db: Session, review_id: int) -> bool:
    review = get_review(db, review_id)
    if not review:
        return False
    db.delete(review)
    db.commit()
    return True

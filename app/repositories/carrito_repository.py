from sqlalchemy.orm import Session
from app.models.carrito_confiteria import CarritoConfiteria
from typing import List, Optional


def get_carrito(db: Session, user_id: int) -> List[CarritoConfiteria]:
    return db.query(CarritoConfiteria).filter(CarritoConfiteria.id_usuario == user_id).all()


def add_item(db: Session, user_id: int, product_id: int, cantidad: int = 1) -> CarritoConfiteria:
    existing = (
        db.query(CarritoConfiteria)
        .filter(CarritoConfiteria.id_usuario == user_id, CarritoConfiteria.id_producto == product_id)
        .first()
    )
    if existing:
        existing.cantidad += cantidad
    else:
        existing = CarritoConfiteria(id_usuario=user_id, id_producto=product_id, cantidad=cantidad)
        db.add(existing)
    db.commit()
    db.refresh(existing)
    return existing


def update_item_cantidad(db: Session, carrito_id: int, cantidad: int) -> Optional[CarritoConfiteria]:
    item = db.query(CarritoConfiteria).filter(CarritoConfiteria.id_carrito == carrito_id).first()
    if not item:
        return None
    item.cantidad = cantidad
    db.commit()
    db.refresh(item)
    return item


def remove_item(db: Session, carrito_id: int) -> bool:
    item = db.query(CarritoConfiteria).filter(CarritoConfiteria.id_carrito == carrito_id).first()
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


def clear_carrito(db: Session, user_id: int):
    db.query(CarritoConfiteria).filter(CarritoConfiteria.id_usuario == user_id).delete()
    db.commit()

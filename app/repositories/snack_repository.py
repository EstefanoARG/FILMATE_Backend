from sqlalchemy.orm import Session
from app.models.snack_category import CategoriaConfiteria
from app.models.snack_product import ProductoConfiteria


def list_categories(db: Session):
    return db.query(CategoriaConfiteria).order_by(CategoriaConfiteria.id_categoria_confi).all()


def list_products(db: Session):
    return db.query(ProductoConfiteria).all()


def get_product(db: Session, product_id: int):
    return db.query(ProductoConfiteria).filter(ProductoConfiteria.id_producto == product_id).first()

import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.snack_category import CategoriaConfiteria
from app.models.snack_product import ProductoConfiteria
from app.schemas.snack import SnackCategoryResponse, SnackProductResponse, CartCalculateRequest, CartCalculateResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/client/snacks", tags=["client snacks"])

@router.get("/categories", response_model=List[SnackCategoryResponse])
def list_categories(db: Annotated[Session, Depends(get_db)]):
    return db.query(CategoriaConfiteria).order_by(CategoriaConfiteria.id_categoria_confi).all()

@router.get("/products", response_model=List[SnackProductResponse])
def list_products(db: Annotated[Session, Depends(get_db)]):
    return db.query(ProductoConfiteria).all()

@router.post("/cart/calculate", response_model=CartCalculateResponse)
def calculate_cart(payload: CartCalculateRequest, db: Annotated[Session, Depends(get_db)]):
    subtotal = 0.0
    for item in payload.items:
        producto = db.query(ProductoConfiteria).filter(ProductoConfiteria.id_producto == item.id_producto).first()
        if producto:
            subtotal += float(producto.precio) * item.cantidad
    return CartCalculateResponse(subtotal=round(subtotal, 2), total=round(subtotal, 2))
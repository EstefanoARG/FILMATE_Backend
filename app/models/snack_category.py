from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base

"""Modelo CategoriaSnack.

Categorías para los productos de snack del cine.
"""

class CategoriaSnack(Base):
    """Entidad `CategoriaSnack`.
    """

    __tablename__ = "categoria_snack"

    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    orden_visual = Column(Integer, default=0)
    estado = Column(Boolean, default=True)

    productos = relationship(
        "ProductoSnack",
        back_populates="categoria"
    )
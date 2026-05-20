from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DECIMAL
)

from sqlalchemy.orm import relationship

from app.core.database import Base

"""Modelo ProductoSnack.

Producto de confitería con precio, categoría y estado.
"""

class ProductoSnack(Base):
    """Entidad `ProductoSnack`.
    """

    __tablename__ = "producto_snack"

    id_producto = Column(Integer, primary_key=True, index=True)

    id_categoria = Column(
        Integer,
        ForeignKey("categoria_snack.id_categoria")
    )

    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255))
    precio_actual = Column(DECIMAL(8, 2), nullable=False)
    url_imagen = Column(String(255), nullable=False)
    is_activo = Column(Boolean, default=True)

    categoria = relationship(
        "CategoriaSnack",
        back_populates="productos"
    )

    reservas = relationship(
        "ReservaSnack",
        back_populates="producto"
    )
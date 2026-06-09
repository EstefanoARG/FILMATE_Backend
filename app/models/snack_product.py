from sqlalchemy import Column, Integer, String, Text, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ProductoConfiteria(Base):
    __tablename__ = "productos_confiteria"

    id_producto = Column(Integer, primary_key=True)
    id_categoria_confi = Column(Integer, ForeignKey("categorias_confiteria.id_categoria_confi", ondelete="SET NULL"))
    nombre_producto = Column(String(100), nullable=False)
    descripcion = Column(Text)
    precio = Column(DECIMAL(10, 2), nullable=False)
    url_imagen = Column(String(255), nullable=False, default="default_snack.png")
    stock = Column(Integer, nullable=False, default=0)

    categoria = relationship("CategoriaConfiteria", back_populates="productos")

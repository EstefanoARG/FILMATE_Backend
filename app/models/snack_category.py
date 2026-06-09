from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class CategoriaConfiteria(Base):
    __tablename__ = "categorias_confiteria"

    id_categoria_confi = Column(Integer, primary_key=True)
    nombre_categoria = Column(String(50), nullable=False)

    productos = relationship("ProductoConfiteria", back_populates="categoria")

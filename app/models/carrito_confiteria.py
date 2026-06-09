from sqlalchemy import Column, Integer, ForeignKey
from app.core.database import Base


class CarritoConfiteria(Base):
    __tablename__ = "carrito_confiteria"

    id_carrito = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"))
    id_producto = Column(Integer, ForeignKey("productos_confiteria.id_producto", ondelete="CASCADE"))
    cantidad = Column(Integer, nullable=False, default=1)

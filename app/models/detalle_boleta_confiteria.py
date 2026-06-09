from sqlalchemy import Column, Integer, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class DetalleBoletaConfiteria(Base):
    __tablename__ = "detalle_boleta_confiteria"

    id_detalle_confi = Column(Integer, primary_key=True, autoincrement=True)
    id_transaccion = Column(Integer, ForeignKey("transacciones.id_transaccion", ondelete="CASCADE"))
    id_producto = Column(Integer, ForeignKey("productos_confiteria.id_producto", ondelete="RESTRICT"))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(DECIMAL(10, 2), nullable=False)

    transaccion = relationship("Transaccion", back_populates="detalle_confiteria")

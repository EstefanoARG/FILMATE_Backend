from sqlalchemy import Column, Integer, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class DetalleBoletaAsiento(Base):
    __tablename__ = "detalle_boleta_asientos"

    id_detalle_asiento = Column(Integer, primary_key=True, autoincrement=True)
    id_transaccion = Column(Integer, ForeignKey("transacciones.id_transaccion", ondelete="CASCADE"))
    id_asiento = Column(Integer, ForeignKey("asientos.id_asiento", ondelete="RESTRICT"))
    ingresado = Column(Boolean, default=False)
    fecha_ingreso = Column(TIMESTAMP, default=None)

    transaccion = relationship("Transaccion", back_populates="detalle_asientos")

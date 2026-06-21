from sqlalchemy import Column, Integer, DECIMAL, String, TIMESTAMP, ForeignKey, text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Transaccion(Base):
    __tablename__ = "transacciones"

    id_transaccion = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="RESTRICT"))
    id_funcion = Column(Integer, ForeignKey("funciones.id_funcion", ondelete="RESTRICT"))
    monto_boletos = Column(DECIMAL(10, 2), nullable=False)
    monto_confiteria = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    monto_total = Column(DECIMAL(10, 2), nullable=False)
    estado_pago = Column(String(20), default="Pendiente")
    metodo_pago = Column(String(50))
    fecha_transaccion = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    detalle_asientos = relationship("DetalleBoletaAsiento", back_populates="transaccion")
    detalle_confiteria = relationship("DetalleBoletaConfiteria", back_populates="transaccion")
    boletas_tickets = relationship("BoletaTicket", back_populates="transaccion")

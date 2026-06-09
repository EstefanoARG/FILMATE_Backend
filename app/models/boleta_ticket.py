from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class BoletaTicket(Base):
    __tablename__ = "boletas_tickets"

    id_ticket = Column(Integer, primary_key=True, autoincrement=True)
    id_transaccion = Column(Integer, ForeignKey("transacciones.id_transaccion", ondelete="CASCADE"))
    codigo_qr_token = Column(String(255), unique=True, nullable=False)
    estado_ticket = Column(String(20), default="Valido")
    fecha_emision = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")

    transaccion = relationship("Transaccion", back_populates="boletas_tickets")

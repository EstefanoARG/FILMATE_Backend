from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, DECIMAL, ForeignKey, text
from app.core.database import Base


class SolicitudReembolso(Base):
    __tablename__ = "solicitudes_reembolso"

    id_reembolso = Column(Integer, primary_key=True)
    id_transaccion = Column(Integer, ForeignKey("transacciones.id_transaccion", ondelete="CASCADE"))
    motivo = Column(Text, nullable=False)
    tipo_reembolso = Column(String(30), nullable=False, default="Reembolso total")
    monto_reembolsado = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    estado_solicitud = Column(String(20), default="Evaluacion")
    comentario_administrador = Column(Text, default=None)
    fecha_solicitud = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    fecha_resolucion = Column(TIMESTAMP, default=None)

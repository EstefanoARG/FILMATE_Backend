from sqlalchemy import Column, Integer, DateTime
from app.core.database import Base


class ReporteContador(Base):
    __tablename__ = "reportes_contador"
    id = Column(Integer, primary_key=True, default=1)
    count = Column(Integer, nullable=False, default=0)
    ultima_generacion = Column(DateTime, nullable=True)

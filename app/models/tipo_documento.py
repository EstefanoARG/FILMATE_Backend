from sqlalchemy import Column, Integer, String
from app.core.database import Base


class TipoDocumento(Base):
    __tablename__ = "tipos_documento"

    id_tipo_doc = Column(Integer, primary_key=True, autoincrement=True)
    siglas = Column(String(10), unique=True, nullable=False)
    descripcion = Column(String(100), nullable=False)

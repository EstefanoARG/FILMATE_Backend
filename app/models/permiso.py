from sqlalchemy import Column, Integer, String
from app.core.database import Base


class Permiso(Base):
    __tablename__ = "permisos"

    id_permiso = Column(Integer, primary_key=True, autoincrement=True)
    codigo_permiso = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(150), nullable=False)
    modulo = Column(String(50), nullable=False)

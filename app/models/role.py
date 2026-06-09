from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base


class Rol(Base):
    __tablename__ = "roles"

    id_role = Column(Integer, primary_key=True)
    nombre_rol = Column(String(50), unique=True, nullable=False)
    descripcion = Column(Text)

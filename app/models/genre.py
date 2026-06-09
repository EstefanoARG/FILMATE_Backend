from sqlalchemy import Column, Integer, String
from app.core.database import Base


class Genero(Base):
    __tablename__ = "generos"

    id_genero = Column(Integer, primary_key=True)
    nombre_genero = Column(String(50), nullable=False)

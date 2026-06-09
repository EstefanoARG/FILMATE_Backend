from sqlalchemy import Column, Integer, ForeignKey
from app.core.database import Base


class RolPermiso(Base):
    __tablename__ = "roles_permisos"

    id_role = Column(Integer, ForeignKey("roles.id_role", ondelete="CASCADE"), primary_key=True)
    id_permiso = Column(Integer, ForeignKey("permisos.id_permiso", ondelete="CASCADE"), primary_key=True)

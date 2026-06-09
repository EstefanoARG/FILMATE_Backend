from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    nombre: str
    username: str
    correo: str
    contrasena: str
    id_tipo_doc: int = 1
    numero_documento: str
    telefono: Optional[str] = None
    url_perfil: Optional[str] = None


class UserUpdate(BaseModel):
    nombre: Optional[str] = None
    username: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    url_perfil: Optional[str] = None
    estado_usuario: Optional[str] = None


class UserLogin(BaseModel):
    correo: str
    contrasena: str


class UserResponse(BaseModel):
    id_usuario: int
    nombre: str
    username: str
    correo: str
    id_tipo_doc: int
    numero_documento: str
    telefono: Optional[str] = None
    url_perfil: Optional[str] = None
    estado_usuario: str
    fecha_registro: Optional[datetime] = None
    ultima_conexion: Optional[datetime] = None
    roles: Optional[List[int]] = None

    @field_validator("roles", mode="before")
    @classmethod
    def normalize_roles(cls, value):
        if value is None:
            return value
        return [getattr(role, "id_role", role) for role in value]

    model_config = {"from_attributes": True}

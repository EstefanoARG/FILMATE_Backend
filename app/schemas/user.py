from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    nombres: str
    apellidos: str
    correo: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    correo: EmailStr
    password: str


class UserResponse(UserBase):
    id_usuario: int
    estado: str
    fecha_registro: datetime

    class Config:
        from_attributes = True
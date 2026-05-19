# backend/app/schemas/genre.py

from pydantic import BaseModel


class GenreBase(BaseModel):
    nombre: str


class GenreCreate(GenreBase):
    pass


class GenreResponse(GenreBase):
    id_genero: int

    class Config:
        from_attributes = True
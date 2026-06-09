from pydantic import BaseModel


class GenreCreate(BaseModel):
    id_genero: int
    nombre_genero: str


class GenreResponse(BaseModel):
    id_genero: int
    nombre_genero: str

    model_config = {"from_attributes": True}

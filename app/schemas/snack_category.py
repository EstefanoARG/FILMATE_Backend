from pydantic import BaseModel


class SnackCategoryBase(BaseModel):
    nombre: str
    orden_visual: int = 0


class SnackCategoryCreate(SnackCategoryBase):
    pass


class SnackCategoryResponse(SnackCategoryBase):
    id_categoria: int
    estado: bool

    class Config:
        from_attributes = True
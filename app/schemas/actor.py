# backend/app/schemas/actor.py

from pydantic import BaseModel


class ActorBase(BaseModel):
    nombre: str


class ActorCreate(ActorBase):
    pass


class ActorResponse(ActorBase):
    id_actor: int

    class Config:
        from_attributes = True
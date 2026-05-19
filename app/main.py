from fastapi import FastAPI

from app.core.database import engine, Base
from app.models import *

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {
        "message": "Filmate API funcionando"
    }
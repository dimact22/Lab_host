from pydantic import BaseModel, Field, validator
from fastapi import FastAPI, HTTPException, status

app = FastAPI()


class Info(BaseModel):
    firstname: str
    lastname: str
    age: int
    gender: str

from pydantic import BaseModel, Field, validator, EmailStr
from fastapi import FastAPI, HTTPException, status
import re


class ContactForm(BaseModel):
    email: EmailStr
    message: str

    @validator('email')
    def email_valid(cls, value):
        pattern = re.compile(
            r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not pattern.match(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid email address'
            )
        return value

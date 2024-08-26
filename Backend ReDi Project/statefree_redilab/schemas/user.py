from pydantic import BaseModel, EmailStr, Field, validator
from typing import Union
from datetime import datetime
import re
from fastapi import Query


class User(BaseModel):
    name: Union[str, None] = Query(default=None,min_length=3, max_length=50)
    email: EmailStr
    phone: Union[str, None] = Query(..., regex=r"^(?:\+?49|0)(?:\d{2}\)?[ -]?\d{2}[ -]?\d{7,8}|\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4})$")
    password: Union[str,None]= Query(min_length=6, max_length=30)
    @validator('password')
    def password_complexity(cls, value):
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', value):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', value):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[@$!%*?&#]', value):
            raise ValueError('Password must contain at least one special character')
        return value
    
    @validator('phone')
    def validate_phone(cls, value):
        if value is not None:
            if not re.match(r"^(?:\+?49|0)(?:\d{2}\)?[ -]?\d{2}[ -]?\d{7,8}|\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4})$", value):
                raise ValueError("Invalid phone number")
        return value


     
class UserLogin(BaseModel):
    name: str
    password: str



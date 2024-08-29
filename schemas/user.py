from pydantic import BaseModel, EmailStr, Field, validator
from fastapi import HTTPException, status
import re


class User(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    phone: str = Field(...)
    password: str = Field(..., min_length=6, max_length=30)
    ort: str

    @validator('password')
    def password_complexity(cls, value):
        if not re.search(r'[A-Z]', value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Password must contain at least one uppercase letter'
            )
        if not re.search(r'[a-z]', value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Password must contain at least one lowercase letter'
            )
        if not re.search(r'[0-9]', value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Password must contain at least one digit'
            )
        if not re.search(r'[@$!%*?&#]', value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Password must contain at least one special character'
            )
        return value

    @validator('email')
    def email_valid(cls, value):
        pattern = re.compile(
            r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not pattern.match(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid email address'
            )
        return value

    @validator('phone')
    def phone_valid(cls, value):
        pattern = re.compile(
            r"^(?:\+?49|0)(?:\d{2}\)?[ -]?\d{2}[ -]?\d{7,8}|\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4})$")
        if not pattern.match(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid phone number. It must be in one of the following formats: '
                '+49 30 12345678, 030 12345678, 030-12345678, or (030) 12345678'
            )
        return value

    @validator('name')
    def name_length(cls, value):
        if len(value) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Name must be at least 3 characters long'
            )
        return value


class UserLogin(BaseModel):
    name: str
    password: str


class DeleteUser(BaseModel):
    name: str


class ChangeUser(BaseModel):
    email: str
    phone: str = Field(...)

    @validator('email')
    def email_valid(cls, value):
        pattern = re.compile(
            r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not pattern.match(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid email address'
            )
        return value

    @validator('phone')
    def phone_valid(cls, value):
        pattern = re.compile(
            r"^(?:\+?49|0)(?:\d{2}\)?[ -]?\d{2}[ -]?\d{7,8}|\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4})$")
        if not pattern.match(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid phone number. It must be in one of the following formats: '
                '+49 30 12345678, 030 12345678, 030-12345678, or (030) 12345678'
            )
        return value

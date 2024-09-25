from pydantic import BaseModel, EmailStr, Field, validator, constr
from fastapi import HTTPException, status
import re

def validate_password(value: str) -> str:
    """Validate password complexity."""
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

class User(BaseModel):
    """Model for user registration."""
    name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr  # Automatically validates the email format
    password: str = Field(..., min_length=6, max_length=30)
    ort: str = Field(..., min_length=2, max_length=100) 

    @validator('password')
    def check_password_complexity(cls, value):
        return validate_password(value)

class UserLogin(BaseModel):
    """Model for user login."""
    email: EmailStr  # Automatically validates the email format
    password: str = Field(..., min_length=6, max_length=30)

    @validator('password')
    def check_password_complexity(cls, value):
        return validate_password(value)

class DeleteUser(BaseModel):
    """Model for deleting a user."""
    email: EmailStr  # Automatically validates the email format

class PdfFile(BaseModel):
    """Model for PDF file creation."""
    name: str
    date: str
    nat: str  # nationality

class ChangeUser(BaseModel):
    """Model for changing user details."""
    name: str

    @validator('name')
    def check_name_length(cls, value):
        if len(value) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Name must be at least 3 characters long'
            )
        return value

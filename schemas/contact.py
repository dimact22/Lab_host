from pydantic import BaseModel, Field, EmailStr, constr
from fastapi import HTTPException, status

class ContactForm(BaseModel):
    email: EmailStr  # Automatically validates the email format
    message: str

    # Optionally, you can add a subject field
    # subject: str = Field(default="No Subject")  

    # If you still want a custom validator for demonstration purposes:
    # @validator('message')
    # def check_message_length(cls, value):
    #     if len(value) < 10:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail='Message must be at least 10 characters long'
    #         )
    #     return value


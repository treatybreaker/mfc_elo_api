from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import EmailStr


class BaseUser(BaseModel):
    username: str = Field(min_length=3,
                          max_length=36)
    email: Optional[EmailStr] = None

    class Config:
        orm_mode = True


class UserPW(BaseUser):
    password: str = Field(min_length=8,
                          regex="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")

    class Config:
        schema_extra = {
            "example": {
                "username": "John Smith",
                "email": "johnsmith@email.com",
                "password": "SomeSecurePassword@321"
            }
        }


class User(BaseUser):
    id: int
    is_active: bool

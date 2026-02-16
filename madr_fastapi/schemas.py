from datetime import datetime

from pydantic import BaseModel, EmailStr


class Message(BaseModel):
    message: str


class AccountSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class AccountPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime


class AccountDB(BaseModel):
    id: int
    username: str
    email: EmailStr
    password: str
    created_at: datetime
    updated_at: datetime


class AccountList(BaseModel):
    accounts: list[AccountPublic]

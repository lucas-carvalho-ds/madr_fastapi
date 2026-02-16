from pydantic import BaseModel, ConfigDict, EmailStr


class Message(BaseModel):
    message: str


class LoginToken(BaseModel):
    token_type: str
    access_token: str


class AccountSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class AccountPublic(BaseModel):
    id: int
    email: EmailStr
    username: str

    model_config = ConfigDict(from_attributes=True)


class AccountList(BaseModel):
    accounts: list[AccountPublic]

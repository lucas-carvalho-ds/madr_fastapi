from pydantic import BaseModel, ConfigDict, EmailStr


class Message(BaseModel):
    message: str


class LoginToken(BaseModel):
    token_type: str
    access_token: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    username: str

    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]

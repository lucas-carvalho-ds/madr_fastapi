from pydantic import BaseModel, ConfigDict, EmailStr, Field


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


class NovelistSchema(BaseModel):
    name: str


class NovelistPublic(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class NovelistUpdate(BaseModel):
    name: str | None = None


class NovelistList(BaseModel):
    novelists: list[NovelistPublic]


class FilterPage(BaseModel):
    limit: int = Field(ge=0, default=20)


class FilterNovelist(FilterPage):
    page: int = 1
    name: str | None = Field(default=None, min_length=1, max_length=80)

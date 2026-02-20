from datetime import datetime

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


class NovelistPublic(NovelistSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class NovelistUpdate(BaseModel):
    name: str | None = None


class NovelistList(BaseModel):
    novelists: list[NovelistPublic]


class PageFilter(BaseModel):
    limit: int = Field(ge=0, default=20)
    page: int = 1


class NovelistFilter(PageFilter):
    name: str | None = Field(default=None, min_length=1, max_length=80)


class BookSchema(BaseModel):
    year: int
    title: str
    novelist_id: int


class BookPublic(BookSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class BookList(BaseModel):
    books: list[BookPublic]


class BookUpdate(BaseModel):
    year: int | None = None
    title: str | None = None
    novelist_id: int | None = None


class BookFilter(PageFilter):
    year: int | None = Field(default=None, ge=1900, le=datetime.now().year)
    title: str | None = Field(default=None, min_length=1, max_length=80)

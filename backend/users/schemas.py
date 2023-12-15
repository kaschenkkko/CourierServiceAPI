"""Pydantic models."""

from pydantic import BaseModel


class RequestUser(BaseModel):
    username: str
    password: str


class ResponseUser(BaseModel):
    id: int
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str

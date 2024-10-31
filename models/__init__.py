from pydantic import BaseModel
from db.models import *

from typing import Optional, List

from tortoise.contrib.pydantic import pydantic_model_creator

# request models
class AuthRequest(BaseModel):
    login: str
    password: str


class EditCardRequest(BaseModel):
    first_name_candidate: Optional[str] = None
    last_name_candidate: Optional[str] = None
    middle_name_candidate: Optional[str] = None
    job_title: Optional[str] = None
    salary: Optional[int] = None
    status: Optional[str] = None
    files: Optional[List[bytes]] = None


class CreateBoardRequest(BaseModel):
    name: str


class CreateCardRequest(BaseModel):
    first_name_candidate: str
    last_name_candidate: str
    middle_name_candidate: str
    job_title: str
    salary: int
    files: Optional[List[bytes]] = None


# response models
class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None


class BaseUser(BaseModel):
    first_name: str
    last_name: str
    middle_name: str



class AuthResponse(BaseResponse):
    token: str
    user: BaseUser


class BoardResponse(BaseResponse):
    board: pydantic_model_creator(Board)
    cards: List[pydantic_model_creator(Card)]


class BoardsResponse(BaseResponse):
    boards: Optional[List[pydantic_model_creator(Board)]] = None


__all__ = (
    "EditCardRequest",
    "AuthRequest",
    "AuthResponse",
    "BaseResponse",
    "BaseUser",
    "BoardResponse",
    "BoardsResponse",
    "CreateBoardRequest",
)
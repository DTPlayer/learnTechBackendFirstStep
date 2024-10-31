from fastapi import APIRouter, Security
from fastapi.responses import JSONResponse
from fastapi_jwt import JwtAuthorizationCredentials

from db.models import *
from models import *

from utils import create_jwt_token, access_security
from datetime import datetime, timezone


router = APIRouter()


@router.post('/auth')
async def auth(auth_data: AuthRequest):
    user = await User.get_or_none(login=auth_data.login,
                                  password=auth_data.password)
    if not user:
        return JSONResponse(status_code=401,
                            content=BaseResponse(success=False,
                                                 message='Неправильный логин или пароль').model_dump(mode='json'))

    token = await Token.get_or_none(user=user)
    if not token:
        jwt_token, subject = await create_jwt_token(user=user)

        await Token.create(
            user=user,
            token=jwt_token,
            expires_at=subject['iat']
        )
    else:
        if token.expires_at < datetime.now(tz=timezone.utc).timestamp():
            jwt_token, subject = await create_jwt_token(user=user)

            await Token.filter(id=token.id).update(
                token=jwt_token,
                expires_at=subject['iat']
            )
        else:
            jwt_token = token.token

    return AuthResponse(
        token=jwt_token,
        user=BaseUser(
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name
        )
    )

@router.get('/board/get/all')
async def get_boards(security: JwtAuthorizationCredentials = Security(access_security)):
    boards = await Board.all().values('id', 'name')

    return BoardsResponse(
        boards=boards
    )


@router.post('/board/create')
async def create_board(board_data: CreateBoardRequest, security: JwtAuthorizationCredentials = Security(access_security)):
    board, _ = await Board.get_or_create(
        name=board_data.name
    )

    cards = await Card.all()

    return BoardResponse(
        board=board,
        cards=cards
    )

__all__ = (
    'router',
)
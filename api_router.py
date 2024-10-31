from fastapi import APIRouter, Security
from fastapi.responses import JSONResponse
from fastapi_jwt import JwtAuthorizationCredentials

from db.models import *
from models import *

from typing import Union
from utils import create_jwt_token
from datetime import datetime, timedelta, timezone


router = APIRouter()


@router.post('/auth')
async def auth(auth_data: AuthRequest) -> Union[JSONResponse, AuthResponse]:
    user = await User.get_or_none(login=auth_data.login,
                                  password=auth_data.password)
    if not user:
        return JSONResponse(status_code=401,
                            content=BaseResponse(success=False,
                                                 message='Неправильный логин или пароль').model_dump(mode='json'))

    token = await Token.get_or_none(user=user)
    if not token:
        token, subject = await create_jwt_token(user=user)

        await Token.create(
            user=user,
            token=token,
            expires_at=subject['expires_at']
        )
    else:
        if token.expires_at < datetime.now(tz=timezone.utc):
            token, subject = await create_jwt_token(user=user)

            await Token.filter(id=token.id).update(
                token=token,
                expires_at=subject['expires_at']
            )

    return AuthResponse(token=token.token,
                        user=user)
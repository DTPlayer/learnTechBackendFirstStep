from typing import Union
from pydantic import UUID4

from fastapi import APIRouter, Security, Response, status, UploadFile, File

from fastapi_jwt import JwtAuthorizationCredentials

from db.models import *
from models import *

from utils import create_jwt_token, access_security
from datetime import datetime, timezone

import os

router = APIRouter()


@router.post('/auth')
async def auth(auth_data: AuthRequest, response: Response) -> Union[AuthResponse, BaseResponse]:
    user = await User.get_or_none(login=auth_data.login,
                                  password=auth_data.password)
    if not user:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return BaseResponse(success=False,
                            message='Неверный логин или пароль')
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
async def get_boards(response: Response, security: JwtAuthorizationCredentials = Security(access_security)) -> Union[BoardsResponse, BaseResponse]:
    user = await User.get_or_none(id=security['user_id'])

    if not user:
        response.status_code = status.HTTP_403_FORBIDDEN
        return BaseResponse(success=False,
                            message='Требуется авторизация')

    boards = await Board.all().values('id', 'name')

    return BoardsResponse(
        boards=boards
    )


@router.post('/board/create')
async def create_board(board_data: CreateBoardRequest, response: Response, security: JwtAuthorizationCredentials = Security(access_security)) -> Union[BoardResponse, BaseResponse]:
    user = await User.get_or_none(id=security['user_id'])

    if not user:
        response.status_code = status.HTTP_403_FORBIDDEN
        return BaseResponse(success=False,
                            message='Требуется авторизация')

    board, _ = await Board.get_or_create(
        name=board_data.name
    )

    cards = await Card.filter(board=board)
    models_cards = list()

    for card in cards:
        card_files = await CardFiles.filter(card=card)
        models_cards.append(BaseCard(
            card=card,
            files=card_files
        ))

    return BoardResponse(
        board=board,
        cards=models_cards,
    )


@router.get('/board/get/{board_id}')
async def get_board(board_id: UUID4, response: Response, security: JwtAuthorizationCredentials = Security(access_security)) -> Union[BoardResponse, BaseResponse]:
    user = await User.get_or_none(id=security['user_id'])

    if not user:
        response.status_code = status.HTTP_403_FORBIDDEN
        return BaseResponse(success=False,
                            message='Требуется авторизация')

    board = await Board.get_or_none(id=board_id)

    if not board:
        response.status_code = status.HTTP_404_NOT_FOUND
        return BaseResponse(success=False,
                            message='Доска не найдена')

    cards = await Card.filter(board=board)

    models_cards = list()

    for card in cards:
        card_files = await CardFiles.filter(card=card)
        models_cards.append(BaseCard(
            card=card,
            files=card_files
        ))

    return BoardResponse(
        board=board,
        cards=models_cards,
    )


@router.post('/card/create')
async def create_card(card_data: CreateCardRequest, response: Response, security: JwtAuthorizationCredentials = Security(access_security)) -> Union[BoardResponse, BaseResponse]:
    user = await User.get_or_none(id=security['user_id'])

    if not user:
        response.status_code = status.HTTP_403_FORBIDDEN
        return BaseResponse(success=False,
                            message='Требуется авторизация')

    board = await Board.get_or_none(id=card_data.board_id)

    if not board:
        response.status_code = status.HTTP_404_NOT_FOUND
        return BaseResponse(success=False,
                            message='Доска не найдена')

    await Card.get_or_create(
        board=board,
        first_name_candidate=card_data.first_name_candidate,
        last_name_candidate=card_data.last_name_candidate,
        middle_name_candidate=card_data.middle_name_candidate,
        job_title=card_data.job_title,
        salary=card_data.salary,
        status=card_data.status,
        hr=user
    )

    cards = await Card.filter(board=board)
    models_cards = list()

    for card in cards:
        card_files = await CardFiles.filter(card=card)
        models_cards.append(BaseCard(
            card=card,
            files=card_files
        ))

    return BoardResponse(
        board=board,
        cards=models_cards,
    )


@router.post('/card/{card_id}/upload')
async def upload_file(card_id: UUID4, response: Response, file: UploadFile, security: JwtAuthorizationCredentials = Security(access_security)) -> Union[BoardResponse, BaseResponse]:
    user = await User.get_or_none(id=security['user_id'])

    if not user:
        response.status_code = status.HTTP_403_FORBIDDEN
        return BaseResponse(success=False,
                            message='Требуется авторизация')

    card = await Card.get_or_none(id=card_id)

    if not card:
        response.status_code = status.HTTP_404_NOT_FOUND
        return BaseResponse(success=False,
                            message='Карточка не найдена')

    if not file.filename.endswith('.docx') and not file.filename.endswith('.xlsx') and not file.filename.endswith('.pdf'):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return BaseResponse(success=False,
                            message='Файл должен быть в формате docx, xlsx, pdf')

    if not os.path.exists('static'):
        os.mkdir('static')

    with open(f'static/{file.filename}', 'wb') as f:
        f.write(file.file.read())

    await CardFiles.get_or_create(
        card=card,
        file_path=f'static/{file.filename}',
        file_metadata={
            'name': file.filename,
            'type': file.content_type,
        }
    )

    cards = await Card.filter(board=(await card.board))

    models_cards = list()

    for card in cards:
        card_files = await CardFiles.filter(card=card)
        models_cards.append(BaseCard(
            card=card,
            files=card_files
        ))

    return BoardResponse(
        board=(await card.board),
        cards=models_cards,
    )


@router.post('/card/{card_id}/edit')
async def edit_card(card_id: UUID4, response: Response, card_data: EditCardRequest, security: JwtAuthorizationCredentials = Security(access_security)) -> Union[BoardResponse, BaseResponse]:
    user = await User.get_or_none(id=security['user_id'])

    if not user:
        response.status_code = status.HTTP_403_FORBIDDEN
        return BaseResponse(success=False,
                            message='Требуется авторизация')

    card = await Card.get_or_none(id=card_id)
    board = await card.board

    if not card:
        response.status_code = status.HTTP_404_NOT_FOUND
        return BaseResponse(success=False,
                            message='Карточка не найдена')

    card_data_dict = card_data.model_dump(mode='json')
    card_data_new_dict = dict()

    for key, value in card_data_dict.items():
        if value:
            card_data_new_dict[key] = value

    card = await card.update_from_dict(data=card_data_new_dict)
    await card.save()

    cards = await Card.filter(board=board)
    models_cards = list()

    for card in cards:
        card_files = await CardFiles.filter(card=card)
        models_cards.append(BaseCard(
            card=card,
            files=card_files
        ))

    return BoardResponse(
        board=board,
        cards=models_cards,
    )


@router.post('/card/{card_id}/delete')
async def delete_card(card_id: UUID4, response: Response, security: JwtAuthorizationCredentials = Security(access_security)) -> Union[BoardResponse, BaseResponse]:
    user = await User.get_or_none(id=security['user_id'])

    if not user:
        response.status_code = status.HTTP_403_FORBIDDEN
        return BaseResponse(success=False,
                            message='Требуется авторизация')

    card = await Card.get_or_none(id=card_id)

    if not card:
        response.status_code = status.HTTP_404_NOT_FOUND
        return BaseResponse(success=False,
                            message='Карточка не найдена')

    await card.delete()

    cards = await Card.filter(board=(await card.board))

    models_cards = list()

    for card in cards:
        card_files = await CardFiles.filter(card=card)
        models_cards.append(BaseCard(
            card=card,
            files=card_files
        ))

    return BoardResponse(
        board=(await card.board),
        cards=models_cards,
    )


@router.post('/board/{board_id}/delete')
async def delete_board(board_id: UUID4, response: Response, security: JwtAuthorizationCredentials = Security(access_security)) -> BaseResponse:
    user = await User.get_or_none(id=security['user_id'])

    if not user:
        response.status_code = status.HTTP_403_FORBIDDEN
        return BaseResponse(success=False,
                            message='Требуется авторизация')

    board = await Board.get_or_none(id=board_id)

    if not board:
        response.status_code = status.HTTP_404_NOT_FOUND
        return BaseResponse(success=False,
                            message='Доска не найдена')

    await board.delete()

    return BaseResponse(success=True)


@router.post('/board/{board_id}/edit')
async def edit_board(board_id: UUID4, board_data: CreateBoardRequest, response: Response, security: JwtAuthorizationCredentials = Security(access_security)) -> Union[BoardResponse, BaseResponse]:
    user = await User.get_or_none(id=security['user_id'])

    if not user:
        response.status_code = status.HTTP_403_FORBIDDEN
        return BaseResponse(success=False,
                            message='Требуется авторизация')

    board = await Board.get_or_none(id=board_id)

    if not board:
        response.status_code = status.HTTP_404_NOT_FOUND
        return BaseResponse(success=False,
                            message='Доска не найдена')

    board.name = board_data.name
    await board.save(update_fields=('name',))

    return BoardResponse(
        board=board,
        cards=list(),
    )

__all__ = (
    'router',
)
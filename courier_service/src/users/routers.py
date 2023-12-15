from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db

from .crud import create_user, get_user
from .schemas import RequestUser, ResponseUser, Token
from .security import create_access_token

user_router = APIRouter()


@user_router.post('/users', response_model=ResponseUser,
                  summary='Регистрация пользователя', tags=['Users'])
async def register_user(user: RequestUser, db: AsyncSession = Depends(get_db)):
    """Регистрация пользователя."""

    db_user = await get_user(db, username=user.username)

    if db_user:
        raise HTTPException(status_code=400, detail='Username already registered')

    return await create_user(db=db, username=user.username, password=user.password)


@user_router.post('/token', response_model=Token,
                  summary='Получение JWT-токена', tags=['Users'])
async def login_for_access_token(
    login_request: RequestUser,
    db: AsyncSession = Depends(get_db)
):
    """Получение JWT-токена."""

    user = await get_user(db, login_request.username)

    if not user or not user.verify_password(login_request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    access_token = create_access_token({'sub': user.username})
    return {'access_token': access_token, 'token_type': 'Bearer'}
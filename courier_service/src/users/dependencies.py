from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db

from .crud import get_user_by_phone_number
from .models import User
from .security import ALGORITHM, SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: AsyncSession = Depends(get_db)
) -> User:
    """Получаем текущего пользователя на основе JWT-токена.

    Args:
        - token (str): JWT-токен для аутентификации пользователя.
        - db (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        - User: Объект пользователя, соответствующий переданному токену.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Не удалось проверить учётные данные.',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone_number: str = payload.get('sub')
        if phone_number is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception

    return await get_user_by_phone_number(db, phone_number)

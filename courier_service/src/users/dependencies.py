from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.delivery.crud import get_courier_by_phone_number
from src.delivery.models import Courier

from .crud import get_user_by_phone_number
from .models import User
from .security import ALGORITHM, SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def get_current_phone_number(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    """Получаем номер телефона текущего пользователя на основе JWT-токена.

    Args:
        - token (str): JWT-токен для аутентификации пользователя.

    Returns:
        - phone_number (str): Номер телефона текущего пользователя/курьера,
                              соответствующий переданному токену.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Не удалось проверить учётные данные.',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone_number: Optional[str] = payload.get('sub')
        if phone_number is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception

    return phone_number


async def get_current_user(
        token=Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:
    """Получаем объект текущего пользователя, из таблицы SQLAlchemy «Пользователи/покупатели»."""

    phone_number: str = await get_current_phone_number(token)
    return await get_user_by_phone_number(db, phone_number)


async def get_current_courier(
        token=Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> Courier:
    """Получаем объект текущего курьера, из таблицы SQLAlchemy «Курьеры»."""

    phone_number: str = await get_current_phone_number(token)
    return await get_courier_by_phone_number(db, phone_number)

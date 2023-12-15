from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User
from .security import get_password_hash


async def create_user(db: AsyncSession, username: str, password: str) -> User:
    """Создаём нового пользователя.

    Args:
        - db (AsyncSession): Асинхронная сессия базы данных SQLAlchemy.
        - username (str): Имя пользователя.
        - password (str): Пароль пользователя.

    Returns:
        - User: Объект пользователя.
    """

    db_user = User(username=username, hashed_password=get_password_hash(password))
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user(db: AsyncSession, username: str) -> Optional[User]:
    """Получаем пользователя из базы данных, по полю «username».

    Args:
        - db (AsyncSession): Асинхронная сессия базы данных SQLAlchemy.
        - username (str): Имя пользователя, которого необходимо найти.

    Returns:
        - Optional[User]: Объект пользователя, если найден, иначе None.
    """

    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalars().first()
    return user

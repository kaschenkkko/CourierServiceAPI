from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.delivery.models import Order

from .models import User
from .security import get_password_hash


async def create_user(
        db: AsyncSession,
        password: str,
        city: Optional[str],
        street: str,
        house_number: str,
        name: str,
        surname: str,
        phone_number: str,
) -> User:
    """Создаём нового пользователя.

    Returns:
        - User: Объект пользователя.
    """

    new_user = User(
        hashed_password=get_password_hash(password),
        city=city,
        street=street,
        house_number=house_number,
        name=name,
        surname=surname,
        phone_number=phone_number,
    )

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError as e:
        if 'check_phone_number' in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Неверный формат номера телефона.'
            )

    return new_user


async def get_user(db: AsyncSession, phone_number: str) -> Optional[User]:
    """Получаем пользователя из базы данных, по полю «phone_number».

    Args:
        - db (AsyncSession): Асинхронная сессия базы данных SQLAlchemy.
        - phone_number (str): Номер телефона пользователя, которого необходимо найти.

    Returns:
        - Optional[User]: Объект пользователя, если найден, иначе None.
    """

    user = await db.execute(select(User).filter(User.phone_number == phone_number))
    return user.scalars().one_or_none()


async def create_order(db: AsyncSession, user_id: int, restaurant_id: int) -> Order:
    """Создаём новый объект в таблице SQLAlchemy «Order».

    Args:
        - db (AsyncSession): Асинхронная сессия базы данных SQLAlchemy.
        - user_id (int): ID текущего пользователя.
        - restaurant_id: ID ресторана, из которого делается заказ.

    Returns:
        - Order: Объект заказа.
    """

    new_order = Order(user_id=user_id, restaurant_id=restaurant_id)

    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)

    return new_order


async def get_active_orders(db: AsyncSession, current_user: User) -> Optional[List[Order]]:
    """Все активные заказы пользователя.

    Получаем объекты из таблицы SQLAlchemy «Order», у которых
    статус заказа находится в состоянии «Поиск курьера» или «В пути».

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - current_user (User): Объект пользователя.

    Returns:
        - Optional[List[Order]]: Список заказов, если найдены, иначе None.
    """

    active_orders = await db.execute(
        select(Order).
        filter(Order.user == current_user,
               Order.status.in_(['В пути', 'Поиск курьера']))
    )
    return active_orders.scalars().all()

from datetime import time
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Order, Restaurant


async def post_restaurant(
        db: AsyncSession,
        name: str,
        opening_time: time,
        closing_time: time,
        duration_delivery: int,
        city: Optional[str],
        street: str,
        house_number: str,

) -> Restaurant:
    """Создаём новый объект в таблице SQLAlchemy «Restaurant».

    Returns:
        - Restaurant: Объект ресторана.
    """

    new_restaurant = Restaurant(
        name=name,
        opening_time=opening_time,
        closing_time=closing_time,
        duration_delivery=duration_delivery,
        city=city,
        street=street,
        house_number=house_number,
    )

    try:
        db.add(new_restaurant)
        await db.commit()
        await db.refresh(new_restaurant)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Такое название ресторана уже существует.'
        )

    return new_restaurant


async def get_restaurant_by_id(db: AsyncSession, id: int) -> Optional[Restaurant]:
    """Получаем один объект из таблицы SQLAlchemy «Restaurant», по значению ID.

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - id (int): ID объекта модели.

    Returns:
        - Optional[Restaurant]: Объект ресторана, если найден, иначе None.
    """

    restaurant = await db.execute(select(Restaurant).filter(Restaurant.id == id))
    return restaurant.scalars().one_or_none()


async def get_order_by_id(db: AsyncSession, order_id: int) -> Optional[Order]:
    """Получаем объект из таблицы SQLAlchemy «Order» по полю «id».

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - current_user (User): Объект пользователя.
        - order_id (int): ID заказа.

    Returns:
        - Optional[Order]: Объект заказа, если найден, иначе None.
    """

    order = await db.execute(select(Order).filter(Order.id == order_id))
    return order.scalars().one_or_none()


async def get_active_restaurant_orders(db: AsyncSession, restaurant_id: int) -> Optional[List[Order]]:
    """Все активные заказы в ресторане.

    Получаем объекты из таблицы SQLAlchemy «Order», у которых
    статус заказа находится в состоянии «Поиск курьера» или «В пути».

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - restaurant_id (int): ID ресторана.

    Returns:
        - Optional[List[Order]]: Список активных заказов, если найдены, иначе None.
    """

    active_orders = await db.execute(
        select(Order).
        filter(Order.restaurant_id == restaurant_id,
               Order.status.in_(['В пути', 'Поиск курьера'])
               ).
        order_by(desc(Order.id))
    )
    return active_orders.scalars().all()

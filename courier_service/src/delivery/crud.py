from datetime import time
from typing import Optional

from sqlalchemy import select
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

    db.add(new_restaurant)
    await db.commit()
    await db.refresh(new_restaurant)

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


async def get_order_from_restaurant_by_id(
        db: AsyncSession,
        restaurant_id: int,
        order_id: int,
) -> Optional[Order]:
    """
    Получаем объект из таблицы SQLAlchemy «Order» по полю «id»
    с определённым полем «restaurant_id»

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - current_user (User): Объект пользователя.
        - restaurant_id (int): ID ресторана.
        - order_id (int): ID заказа.

    Returns:
        - Optional[Order]: Объект заказа, если найден, иначе None.
    """

    order = await db.execute(
        select(Order).
        filter(Order.id == order_id,
               Order.restaurant_id == restaurant_id)
    )
    return order.scalars().one_or_none()

from datetime import datetime, time
from typing import List, Optional

import pytz
from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.configs import TIMEZONE
from src.users.security import get_password_hash

from .models import Courier, Order, Restaurant


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


async def get_restaurant_by_id(db: AsyncSession, restaurant_id: int) -> Optional[Restaurant]:
    """Получаем один объект из таблицы SQLAlchemy «Restaurant» по полю «id».

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - restaurant_id (int): ID ресторана.

    Returns:
        - Optional[Restaurant]: Объект ресторана, если найден, иначе None.
    """

    restaurant = await db.execute(select(Restaurant).filter(Restaurant.id == restaurant_id))
    return restaurant.scalars().one_or_none()


async def get_order_by_id(db: AsyncSession, order_id: int) -> Optional[Order]:
    """Получаем объект из таблицы SQLAlchemy «Order» по полю «id».

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - order_id (int): ID заказа.

    Returns:
        - Optional[Order]: Объект заказа, если найден, иначе None.
    """

    order = await db.execute(select(Order).filter(Order.id == order_id))
    return order.scalars().one_or_none()


async def get_active_restaurant_orders(db: AsyncSession, restaurant_id: int) -> Optional[List[Order]]:
    """Все активные заказы в ресторане.

    Получаем объекты из таблицы SQLAlchemy «Order», для определённого ресторана, у которых
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


async def create_courier(
        db: AsyncSession,
        password: str,
        name: str,
        surname: str,
        phone_number: str,
) -> Courier:
    """Создаём новый объект в таблице SQLAlchemy «Courier».

    Returns:
        - Courier: Объект курьера.
    """

    new_courier = Courier(
        hashed_password=get_password_hash(password),
        name=name,
        surname=surname,
        phone_number=phone_number,
    )

    try:
        db.add(new_courier)
        await db.commit()
        await db.refresh(new_courier)
    except IntegrityError as e:
        if 'check_phone_number' in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Неверный формат номера телефона.'
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Курьер уже зарегестрирован.'
        )

    return new_courier


async def get_courier_by_phone_number(db: AsyncSession, phone_number: str) -> Optional[Courier]:
    """Получаем курьера из базы данных, по полю «phone_number».

    Args:
        - db (AsyncSession): Асинхронная сессия базы данных SQLAlchemy.
        - phone_number (str): Номер телефона курьера, которого необходимо найти.

    Returns:
        - Optional[Courier]: Объект пользователя, если найден, иначе None.
    """

    courier = await db.execute(select(Courier).filter(Courier.phone_number == phone_number))
    return courier.scalars().one_or_none()


async def get_all_available_couriers_orders(db: AsyncSession) -> Optional[List[Order]]:
    """Все свободные заказы для курьеров, из всех ресторанов.

    Получаем объекты из таблицы SQLAlchemy «Order», у которых
    статус заказа находится в состоянии «Поиск курьера».

    Args:
        - db (AsyncSession): Асинхронная сессия для подключения к БД.

    Returns:
        - Optional[List[Order]]: Список свободных заказов, если найдены, иначе None.
    """

    active_orders = await db.execute(
        select(Order).
        filter(Order.status == 'Поиск курьера').
        order_by(Order.id)
    )
    return active_orders.scalars().all()


async def get_active_courier_order(
        db: AsyncSession,
        current_courier: Courier
) -> List[Optional[Order]]:
    """Активный заказ для курьера.

    Получаем объект из таблицы SQLAlchemy «Order», для текущего курьера,
    у которого статус заказа находится в состоянии «В пути».

    Args:
        - current_courier (Courier): Объект курьера.
        - db (AsyncSession): Асинхронная сессия для подключения к БД.

    Returns:
        - Optional[Order]: Активный заказ, если найден, иначе None.
    """

    courier_order = await db.execute(
        select(Order).
        filter(
            Order.courier_id == current_courier.id,
            Order.status == 'В пути'
            ).
        order_by(desc(Order.id))
    )
    return courier_order.scalars().all()


async def post_active_courier_order_by_id(
        db: AsyncSession,
        current_courier: Courier,
        order_id: int
) -> None:
    """Обрабатываем запрос на взятие заказа в работу.

    - Получаем выбранный курьером заказ, меняем статус заказа на статус «В пути»
    и добавляем объект курьера в данный заказ.
    - Меняем статус работы курьера на статус «Выполняет заказ».

    Args:
        - current_courier (Courier): Объект курьера.
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - order_id (int): ID заказа.
    """

    courier_order = await db.execute(
        select(Order).
        filter(
            Order.status == 'Поиск курьера',
            Order.id == order_id
        )
    )
    courier_order: Optional[Order] = courier_order.scalars().one_or_none()

    if not courier_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Заказ с таким ID не найден.'
        )

    courier_order.status = 'В пути'
    courier_order.courier_id = current_courier.id
    current_courier.status = 'Выполняет заказ'

    await db.commit()
    await db.refresh(courier_order)
    await db.refresh(current_courier)


async def put_active_courier_order_by_id(
        db: AsyncSession,
        current_courier: Courier,
        order_id: int
) -> None:
    """Обрабатываем запрос на завершение заказа.

    - Получаем выбранный курьером заказ, меняем статус заказа на статус «Доставлен»,
    добавляем текущее время в поле «end_time».
    - Меняем статус работы курьера на статус «Без заказа».

    Args:
        - current_courier (Courier): Объект курьера.
        - db (AsyncSession): Асинхронная сессия для подключения к БД.
        - order_id (int): ID заказа.
    """

    courier_order = await db.execute(
        select(Order).
        filter(
            Order.courier_id == current_courier.id,
            Order.status == 'В пути',
            Order.id == order_id
        )
    )

    courier_order: Optional[Order] = courier_order.scalars().one_or_none()

    if not courier_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Заказ с таким ID не найден.'
        )

    courier_order.status = 'Доставлен'
    courier_order.end_time = datetime.now(pytz.timezone(TIMEZONE)).replace(microsecond=0)
    current_courier.status = 'Без заказа'

    await db.commit()
    await db.refresh(courier_order)
    await db.refresh(current_courier)

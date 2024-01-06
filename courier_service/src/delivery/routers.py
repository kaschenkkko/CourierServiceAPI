from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.users.dependencies import get_current_courier
from src.users.models import User
from src.users.schemas import CreateTokenPyd, ResponseTokenPyd, UserInfoPyd
from src.users.security import create_access_token

from .crud import (create_courier, get_active_courier_order,
                   get_active_restaurant_orders,
                   get_all_available_couriers_orders,
                   get_courier_by_phone_number, get_order_by_id,
                   get_restaurant_by_id, post_active_courier_order_by_id,
                   post_restaurant, put_active_courier_order_by_id)
from .exceptions import raise_forbidden_if_not_courier
from .models import Courier, Order, Restaurant
from .schemas import (CourierOrdersInfoPyd, CreateCourierPyd,
                      DetailedRestaurantInfoPyd, DetailedRestaurantOrderPyd,
                      ResponseRestaurantPyd, SummaryRestaurantOrderPyd)

delivery_router = APIRouter()


@delivery_router.post('/api/v1/restaurants', response_model=ResponseRestaurantPyd,
                      summary='Добавить ресторан', tags=['Рестораны'],  status_code=201)
async def create_restaurant(
    restaurant: DetailedRestaurantInfoPyd,
    db: AsyncSession = Depends(get_db),
) -> Restaurant:

    restaurant_data = restaurant.model_dump()

    return await post_restaurant(db=db, **restaurant_data)


@delivery_router.get('/api/v1/restaurants/{restaurant_id}/orders',
                     response_model=List[SummaryRestaurantOrderPyd],
                     summary='Заказы ресторана', tags=['Рестораны'])
async def get_restaurant_orders(
    db: AsyncSession = Depends(get_db),
    restaurant_id: int = Path(..., description='ID ресторана'),
    active: Optional[str] = Query(None, description='Выводим только активные заказы ресторана.')
) -> Optional[List[Order]]:
    """
    По умолчанию выводятся все заказы ресторана, но вы можете передать параметр запроса «active»,
    что-бы получить список только активных заказов, у которых статус заказа находится в
    состоянии «Поиск курьера» или «В пути».
    """

    restaurant: Optional[Restaurant] = await get_restaurant_by_id(db, restaurant_id)

    if restaurant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Ресторан с таким ID не найден.',
        )

    if active is not None:
        return await get_active_restaurant_orders(db, restaurant_id)
    return restaurant.orders


@delivery_router.get('/api/v1/restaurants/{restaurant_id}/orders/{order_id}',
                     response_model=DetailedRestaurantOrderPyd,
                     summary='Информация о заказе', tags=['Рестораны'])
async def get_restaurant_order(
    db: AsyncSession = Depends(get_db),
    restaurant_id: int = Path(..., description='ID ресторана'),
    order_id: int = Path(..., description='ID заказа'),
) -> DetailedRestaurantOrderPyd:
    """Подробная информация об одном выбранном заказе ресторана."""

    order: Optional[Order] = await get_order_by_id(db, order_id)

    if order is None or order.restaurant_id != restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Заказ с такими значениями «restaurant_id» и «order_id» не найден.',
        )

    user: User = order.user
    courier: Courier = order.courier
    courier_data: Optional[Dict] = courier.__dict__ if courier else None

    result = DetailedRestaurantOrderPyd(
        id=order.id,
        status=order.status,
        start_time=order.start_time,
        restaurant_id=order.restaurant_id,
        end_time=order.end_time,
        courier=courier_data,
        user=user.__dict__
    )

    return result


@delivery_router.post('/api/v1/couriers', response_model=UserInfoPyd,  status_code=201,
                      summary='Регистрация курьера', tags=['Курьеры'])
async def register_couriers(
    courier: CreateCourierPyd,
    db: AsyncSession = Depends(get_db)
) -> Courier:

    courier_data = courier.model_dump()

    return await create_courier(db=db, **courier_data)


@delivery_router.post('/api/v1/couriers/token', response_model=ResponseTokenPyd,
                      summary='Получение токена для курьеров', tags=['Курьеры'])
async def login_for_courier_access_token(
    login_request: CreateTokenPyd,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:

    courier: Optional[Courier] = await get_courier_by_phone_number(db, login_request.phone_number)

    if not courier or not courier.verify_password(login_request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный номер телефона или пароль.',
        )

    access_token: str = create_access_token({'sub': courier.phone_number})
    return {'access_token': access_token, 'token_type': 'Bearer'}


@delivery_router.get('/api/v1/couriers/available_orders', response_model=List[CourierOrdersInfoPyd],
                     summary='Свободные заказы', tags=['Курьеры'])
async def available_couriers_orders(
    current_courier: Courier = Depends(get_current_courier),
    db: AsyncSession = Depends(get_db),
) -> Optional[List[Order]]:
    """Выводим список всех заказов, из всех рестаранов, которые могут взять курьеры."""

    raise_forbidden_if_not_courier(current_courier)

    return await get_all_available_couriers_orders(db)


@delivery_router.get('/api/v1/couriers/orders',
                     response_model=List[CourierOrdersInfoPyd],
                     summary='Заказы курьера', tags=['Курьеры'])
async def courier_orders(
    current_courier: Courier = Depends(get_current_courier),
    db: AsyncSession = Depends(get_db),
    all_orders: Optional[str] = Query(None, description='Выводим все заказы курьера.')
) -> List[Optional[Order]]:
    """
    По умолчанию выводится только активный заказ курьера, у которого статус
    заказа «В пути». Но вы можете передать параметр запроса «all_orders»,
    что-бы получить список всех заказов, которые выполнял/выполняет курьер.
    """

    if all_orders is not None:
        return current_courier.orders
    return await get_active_courier_order(db, current_courier)


@delivery_router.post('/api/v1/couriers/orders/{order_id}', status_code=204,
                      summary='Взять заказ', tags=['Курьеры'])
async def courier_accepts_order(
    current_courier: Courier = Depends(get_current_courier),
    db: AsyncSession = Depends(get_db),
    order_id: int = Path(..., description='ID заказа'),
) -> None:
    """Курьер берёт в работу выбранный заказ."""

    if await get_active_courier_order(db, current_courier):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='У вас уже есть один заказ.',
        )

    await post_active_courier_order_by_id(db, current_courier, order_id)


@delivery_router.put('/api/v1/couriers/orders/{order_id}', status_code=204,
                     summary='Завершить заказ', tags=['Курьеры'])
async def courier_completes_order(
    current_courier: Courier = Depends(get_current_courier),
    db: AsyncSession = Depends(get_db),
    order_id: int = Path(..., description='ID заказа'),
) -> None:
    """Курьер завершает выбранный заказ."""

    await put_active_courier_order_by_id(db, current_courier, order_id)

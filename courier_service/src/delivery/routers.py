from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.users.dependencies import get_current_user
from src.users.models import User

from .crud import (get_active_restaurant_orders, get_order_by_id,
                   get_restaurant_by_id, post_restaurant)
from .models import Courier, Order, Restaurant
from .schemas import (CreateRestaurantPyd, DetailedRestaurantOrderPyd,
                      ResponseRestaurantPyd, SummaryRestaurantOrderPyd)

delivery_router = APIRouter()


@delivery_router.post('/api/v1/restaurants', response_model=ResponseRestaurantPyd,
                      summary='Добавить ресторан', tags=['Рестораны'])
async def create_restaurant(
    restaurant: CreateRestaurantPyd,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Restaurant:

    restaurant_data = restaurant.dict()

    return await post_restaurant(db=db, **restaurant_data)


@delivery_router.get('/api/v1/restaurants/{restaurant_id}/orders',
                     response_model=List[SummaryRestaurantOrderPyd],
                     summary='Заказы ресторана', tags=['Рестораны'])
async def get_restaurant_orders(
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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

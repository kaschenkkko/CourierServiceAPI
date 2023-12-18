from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.users.dependencies import get_current_user
from src.users.models import User

from .crud import get_restaurant_by_id, post_restaurant
from .schemas import (CreateRestaurantPyd, DetailedRestaurantOrderPyd,
                      ResponseRestaurantPyd, SummaryRestaurantOrderPyd)

delivery_router = APIRouter()


@delivery_router.post('/api/v1/restaurants', response_model=ResponseRestaurantPyd,
                      summary='Создать ресторан', tags=['Рестораны'])
async def create_restaurant(
    restaurant: CreateRestaurantPyd,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создать ресторан."""

    restaurant_data = restaurant.dict()

    try:
        return await post_restaurant(db=db, **restaurant_data)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Такое название ресторана уже существует.'
        )


@delivery_router.get('/api/v1/restaurants/{restaurant_id}/orders',
                     response_model=List[SummaryRestaurantOrderPyd],
                     summary='Все заказы из выбранного ресторана', tags=['Рестораны'])
async def get_all_restaurant_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    restaurant_id: int = Path(..., description='ID ресторана'),
):
    """Все заказы ресторана."""

    restaurant = await get_restaurant_by_id(db, restaurant_id)
    return restaurant.orders


@delivery_router.get('/api/v1/restaurants/{restaurant_id}/orders/{order_id}',
                     response_model=DetailedRestaurantOrderPyd,
                     summary='Подробная информация об выбранном заказе', tags=['Рестораны'])
async def get_restaurant_order(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    restaurant_id: int = Path(..., description='ID ресторана'),
    order_id: int = Path(..., description='ID заказа'),
):
    """Подробная информация об выбранном заказе."""

    pass

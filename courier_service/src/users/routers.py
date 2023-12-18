from random import randrange
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.delivery.crud import get_restaurant_by_id
from src.delivery.models import Order
from src.delivery.schemas import (BaseOrderPyd, ResponseUserCreateOrderPyd,
                                  ShippingCostPyd)

from .crud import (create_order, create_user, get_active_orders,
                   get_user_by_phone_number)
from .dependencies import get_current_user
from .models import User
from .schemas import (CreateTokenPyd, CreateUserPyd, ResponseTokenPyd,
                      ResponseUserPyd)
from .security import create_access_token

user_router = APIRouter()


@user_router.post('/api/v1/users', response_model=ResponseUserPyd,
                  summary='Регистрация пользователя', tags=['Авторизация'])
async def register_user(user: CreateUserPyd, db: AsyncSession = Depends(get_db)):
    """Регистрация пользователя."""

    user_data = user.dict()
    db_user = await get_user_by_phone_number(db, user.phone_number)

    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Пользователь уже зарегестрирован.'
        )

    return await create_user(db=db, **user_data)


@user_router.post('/api/v1/token', response_model=ResponseTokenPyd,
                  summary='Получение токена', tags=['Авторизация'])
async def login_for_access_token(login_request: CreateTokenPyd, db: AsyncSession = Depends(get_db)):
    """Получение токена."""

    user = await get_user_by_phone_number(db, login_request.phone_number)

    if not user or not user.verify_password(login_request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный номер телефона или пароль.',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    access_token = create_access_token({'sub': user.phone_number})
    return {'access_token': access_token, 'token_type': 'Bearer'}


@user_router.get('/api/v1/users/orders', response_model=List[BaseOrderPyd],
                 summary='Все заказы пользователя', tags=['Пользователи'])
async def get_all_user_orders(current_user: User = Depends(get_current_user)):
    """Все заказы пользователя."""

    return current_user.orders


@user_router.get('/api/v1/shipping_cost/{restaurant_id}', response_model=ShippingCostPyd,
                 summary='Расчёт стоимости доставки', tags=['Пользователи'])
async def shipping_cost(
    restaurant_id: int = Path(..., description='ID ресторана'),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Расчёт стоимости доставки из выбранного ресторана."""

    restaurant = await get_restaurant_by_id(db, restaurant_id)

    if restaurant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Ресторан с таким ID не найден.',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    if restaurant.street == current_user.street:
        return {'shipping_cost': 50}

    return {'shipping_cost': randrange(200, 500)}


@user_router.post('/api/v1/users/orders/{restaurant_id}', response_model=ResponseUserCreateOrderPyd,
                  summary='Сделать заказ из ресторана', tags=['Пользователи'])
async def new_order(
    restaurant_id: int = Path(..., description='ID ресторана'),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Сделать заказ из ресторана."""

    order_info = await create_order(db, current_user.id, restaurant_id)
    shipping_cost_value = await shipping_cost(restaurant_id, current_user, db)

    result = ResponseUserCreateOrderPyd.parse_obj({**order_info.__dict__, **shipping_cost_value})
    return result


@user_router.get('/api/v1/users/active_orders', response_model=List[BaseOrderPyd],
                 summary='Активные заказы пользователя', tags=['Пользователи'])
async def active_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Optional[List[Order]]:
    """
    Информация об активных заказах пользователя. Статус заказа
    находится в состоянии «Поиск курьера» или «В пути».
    """

    return await get_active_orders(db, current_user)

from random import randrange
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.delivery.crud import get_order_by_id, get_restaurant_by_id
from src.delivery.models import Order, Restaurant
from src.delivery.schemas import (BaseOrderPyd, ResponseUserCreateOrderPyd,
                                  ShippingCostPyd)

from .crud import (create_order, create_user, get_active_user_orders,
                   get_user_by_phone_number)
from .dependencies import get_current_user
from .models import User
from .schemas import (CreateTokenPyd, CreateUserPyd, DetailedUserOrderPyd,
                      ResponseTokenPyd, ResponseUserPyd)
from .security import create_access_token

user_router = APIRouter()


@user_router.post('/api/v1/users', response_model=ResponseUserPyd,
                  summary='Регистрация пользователя', tags=['Авторизация'])
async def register_user(user: CreateUserPyd, db: AsyncSession = Depends(get_db)) -> User:

    user_data = user.dict()
    db_user: Optional[User] = await get_user_by_phone_number(db, user.phone_number)

    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Пользователь уже зарегестрирован.'
        )

    return await create_user(db=db, **user_data)


@user_router.post('/api/v1/token', response_model=ResponseTokenPyd,
                  summary='Получение токена', tags=['Авторизация'])
async def login_for_access_token(
    login_request: CreateTokenPyd,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:

    user: Optional[User] = await get_user_by_phone_number(db, login_request.phone_number)

    if not user or not user.verify_password(login_request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный номер телефона или пароль.',
        )

    access_token: str = create_access_token({'sub': user.phone_number})
    return {'access_token': access_token, 'token_type': 'Bearer'}


@user_router.get('/api/v1/users/orders', response_model=List[BaseOrderPyd],
                 summary='Заказы пользователя', tags=['Пользователи'])
async def get_user_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    active: Optional[str] = Query(None, description='Выводим только активные заказы пользователя.')
) -> Optional[List[Order]]:
    """
    По умолчанию выводятся все заказы пользователя, но вы можете передать параметр запроса «active»,
    что-бы получить список только активных заказов, у которых статус заказа находится в
    состоянии «Поиск курьера» или «В пути».
    """

    if active is not None:
        return await get_active_user_orders(db, current_user)
    return current_user.orders


@user_router.get('/api/v1/users/orders/get/{order_id}', response_model=DetailedUserOrderPyd,
                 summary='Информация о заказе', tags=['Пользователи'])
async def get_user_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DetailedUserOrderPyd:
    """Подробная информация об одном выбранном заказе пользователя."""

    user_order: Optional[Order] = await get_order_by_id(db, order_id)

    if user_order is None or user_order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='В вашем списке заказов нет заказа с таким значением «order_id».',
        )

    courier = user_order.courier
    courier_name: Optional[str] = user_order.courier.__dict__.get('name') if courier else None

    result = DetailedUserOrderPyd(
        id=user_order.id,
        status=user_order.status,
        restaurant_name=user_order.restaurant.__dict__.get('name'),
        start_time=user_order.start_time,
        end_time=user_order.end_time,
        courier_name=courier_name,
        duration_delivery=user_order.restaurant.__dict__.get('duration_delivery'),
    )

    return result


@user_router.get('/api/v1/users/shipping_cost/{restaurant_id}', response_model=ShippingCostPyd,
                 summary='Стоимость доставки', tags=['Пользователи'])
async def shipping_cost(
    restaurant_id: int = Path(..., description='ID ресторана'),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, int]:
    """Расчёт стоимости доставки из выбранного ресторана."""

    restaurant: Optional[Restaurant] = await get_restaurant_by_id(db, restaurant_id)

    if restaurant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Ресторан с таким ID не найден.',
        )

    if restaurant.street == current_user.street:
        return {'shipping_cost': 50}

    return {'shipping_cost': randrange(200, 500)}


@user_router.post('/api/v1/users/orders/post/{restaurant_id}', response_model=ResponseUserCreateOrderPyd,
                  summary='Сделать заказ', tags=['Пользователи'])
async def new_order(
    restaurant_id: int = Path(..., description='ID ресторана'),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResponseUserCreateOrderPyd:
    """Сделать заказ из выбранного ресторана."""

    order_info: Order = await create_order(db, current_user.id, restaurant_id)
    shipping_cost_value: Dict[str, int] = await shipping_cost(restaurant_id, current_user, db)

    result = ResponseUserCreateOrderPyd.parse_obj({**order_info.__dict__, **shipping_cost_value})
    return result

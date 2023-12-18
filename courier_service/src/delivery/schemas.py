"""Pydantic models."""

from datetime import datetime, time
from typing import Optional

from pydantic import BaseModel, Field
from src.users.schemas import BaseAddressPyd, BaseUserDataPyd, ResponseUserPyd


class CreateRestaurantPyd(BaseAddressPyd):
    """Pydantic модель для создания ресторана.

    Fields:
        - name: str
        - opening_time: time
        - closing_time: time
        - duration_delivery: int
        - city: Optional[str]
        - street: str
        - house_number: str
    """

    name: str = Field(description='Название ресторана')
    opening_time: time = Field(description='Время открытия ресторана')
    closing_time: time = Field(description='Время закрытия ресторана')
    duration_delivery: int = Field(description='Примерное время доставки заказа/в минутах')


class ResponseRestaurantPyd(BaseModel):
    """Pydantic модель для вывода информации о ресторане, после его создания.

    Fields:
        - id: int
        - name: int
    """

    id: int = Field(description='ID объекта в БД')
    name: str = Field(description='Название ресторана')


class BaseOrderPyd(BaseModel):
    """Pydantic модель с базовыми полями для информации о заказе.

    Fields:
        - id: int
        - status: int
        - start_time: datetime
        - restaurant_id: int
    """

    id: int = Field(description='ID объекта в БД')
    status: str = Field(description='Статус заказа')
    start_time: datetime = Field(description='Время создания заказа')
    restaurant_id: int = Field(description='ID ресторана, из которого сделан заказ')


class SummaryRestaurantOrderPyd(BaseOrderPyd):
    """Pydantic модель с краткой информацией о заказах ресторана.

    Fields:
        - id: int
        - status: int
        - start_time: datetime
        - restaurant_id: int
        - courier_id: Optional[int]
        - user_id: int
    """

    courier_id: Optional[int] = Field(None, description='ID курьера')
    user_id: int = Field(description='ID пользователя, который сделал заказ')


class DetailedUserInfoPyd(BaseUserDataPyd, BaseAddressPyd):
    """Pydantic модель для вывода  подробной информации о пользователе.

    Fields:
        - id: int
        - city: Optional[str]
        - street: str
        - house_number: str
        - phone_number: str
        - name: str
        - surname: str
    """

    id: int = Field(description='ID объекта в БД')


class DetailedRestaurantOrderPyd(BaseOrderPyd):
    """Pydantic модель с подробной информацией о заказе ресторана.

    Fields:
        - id: int
        - status: int
        - start_time: datetime
        - restaurant_id: int
        - end_time: datetime
        - courier: Optional[ResponseUserPyd]
        - user: DetailedUserInfoPyd
    """

    end_time: datetime = Field(description='Время завершения доставки')
    courier: Optional[ResponseUserPyd] = Field(None, description='Курьер')
    user: DetailedUserInfoPyd = Field(description='Пользователь который сделал заказ')


class ShippingCostPyd(BaseModel):
    """Pydantic модель для расчёта стоимости доставки.

    Fields:
        - shipping_cost: int
    """

    shipping_cost: int = Field(description='Стоимость доставки из ресторана')


class ResponseUserCreateOrderPyd(BaseOrderPyd, ShippingCostPyd):
    """Pydantic модель для вывода информации о заказе, после его создания.

    Fields:
        - id: int
        - status: int
        - start_time: datetime
        - restaurant_id: int
        - shipping_cost: int
    """
    pass

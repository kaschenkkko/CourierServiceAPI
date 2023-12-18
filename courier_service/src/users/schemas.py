"""Pydantic models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RequestUserPyd(BaseModel):
    phone_number: str = Field(description='Телефон пользователя')
    name: str = Field(description='Имя пользователя')
    surname: str = Field(description='Фамилия пользователя')
    password: str = Field(description='Пароль пользователя')
    city: Optional[str] = Field('Тюмень', description='Город пользователя')
    street: str = Field(description='Улица пользователя')
    house_number: str = Field(description='Номер дома пользователя')


class ResponseUserPyd(BaseModel):
    id: int = Field(description='ID объекта в БД')
    name: str = Field(description='Имя пользователя')
    surname: str = Field(description='Фамилия пользователя')
    phone_number: str = Field(description='Телефон пользователя')


class TokenPyd(BaseModel):
    access_token: str = Field(description='Токен')
    token_type: str = Field(description='Тип токена')


class CreateTokenPyd(BaseModel):
    phone_number: str = Field(description='Телефон пользователя')
    password: str = Field(description='Пароль пользователя')


class ShippingCostPyd(BaseModel):
    shipping_cost: int = Field(description='Стоимость доставки из ресторана')


class BaseOrdersPyd(BaseModel):
    id: int = Field(description='ID объекта в БД')
    status: str = Field(description='Статус заказа')
    start_time: datetime = Field(description='Время создания заказа')
    restaurant_id: int = Field(description='ID ресторана, из которого сделан заказ')


class ResponseCreateOrderPyd(BaseOrdersPyd, ShippingCostPyd):
    pass


class RequestCreateOrderPyd(BaseModel):
    """Получаем ID ресторана для создания заказа или расчёта стоимости доставки."""

    restaurant_id: int = Field(description='ID ресторана')

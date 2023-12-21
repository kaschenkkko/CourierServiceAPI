"""Pydantic models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CreateTokenPyd(BaseModel):
    """Pydantic модель для создания токена.

    Fields:
        - phone_number: str
        - password: str
    """

    phone_number: str = Field(description='Номер телефона')
    password: str = Field(description='Пароль для входа')


class ResponseTokenPyd(BaseModel):
    """Pydantic модель для вывода токена.

    Fields:
        - access_token: str
        - token_type: str
    """

    access_token: str = Field(description='Токен')
    token_type: str = Field(description='Тип токена')


class BaseAddressPyd(BaseModel):
    """Pydantic модель с базовыми полями для адреса.

    Fields:
        - city: Optional[str]
        - street: str
        - house_number: str
    """

    city: Optional[str] = Field('Тюмень', description='Город')
    street: str = Field(description='Улица')
    house_number: str = Field(description='Номер дома')


class BaseUserDataPyd(BaseModel):
    """Pydantic модель с базовыми полями для пользователя/курьера.

    Fields:
        - phone_number: str
        - name: str
        - surname: str
    """

    phone_number: str = Field(description='Номер телефона')
    name: str = Field(description='Имя')
    surname: str = Field(description='Фамилия')


class CreateUserPyd(BaseUserDataPyd, BaseAddressPyd):
    """Pydantic модель для регистрации пользователя.

    Fields:
        - city: Optional[str]
        - street: str
        - house_number: str
        - phone_number: str
        - name: str
        - surname: str
        - password: str
    """

    password: str = Field(description='Пароль пользователя')


class UserInfoPyd(BaseUserDataPyd):
    """Pydantic модель для вывода информации о пользователе/курьере.

    Fields:
        - id: int
        - phone_number: str
        - name: str
        - surname: str
    """

    id: int = Field(description='ID объекта в БД')


class DetailedUserOrderPyd(BaseModel):
    """Pydantic модель с подробной информацией о заказе для пользователя.

    Fields:
        - id: int
        - status: str
        - restaurant_name: str
        - start_time: datetime
        - end_time: Optional[datetime]
        - courier_name: Optional[str]
        - duration_delivery: int
    """
    id: int = Field(description='ID заказа в БД')
    status: str = Field(description='Статус заказа')
    restaurant_name: str = Field(description='Название ресторана, из которого сделан заказ')
    start_time: datetime = Field(description='Время создания заказа')
    end_time: Optional[datetime] = Field(None, description='Время завершения доставки')
    courier_name: Optional[str] = Field(None, description='Имя курьера')
    duration_delivery: int = Field(description='Примерное время доставки заказа/в минутах')

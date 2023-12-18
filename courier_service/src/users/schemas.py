"""Pydantic models."""

from typing import Optional

from pydantic import BaseModel, Field


class CreateTokenPyd(BaseModel):
    """Pydantic модель для создания токена."""

    phone_number: str = Field(description='Телефон пользователя')
    password: str = Field(description='Пароль пользователя')


class ResponseTokenPyd(BaseModel):
    """Pydantic модель для вывода токена."""

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
    """Pydantic модель с базовыми полями для пользователя.

    Fields:
        - phone_number: str
        - name: str
        - surname: str
    """

    phone_number: str = Field(description='Телефон пользователя')
    name: str = Field(description='Имя пользователя')
    surname: str = Field(description='Фамилия пользователя')


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


class ResponseUserPyd(BaseUserDataPyd):
    """Pydantic модель для вывода информации о пользователе.

    Fields:
        - id: int
        - phone_number: str
        - name: str
        - surname: str
    """

    id: int = Field(description='ID объекта в БД')


class UserCreateOrderPyd(BaseModel):
    """Pydantic модель  для создания заказа.

    Fields:
        - restaurant_id: int
    """

    restaurant_id: int = Field(description='ID ресторана')

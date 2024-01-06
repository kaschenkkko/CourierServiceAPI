from datetime import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy import insert, select
from src.delivery.models import Order, Restaurant

from .conftest import async_session_maker


@pytest.mark.asyncio(scope='session')
async def test_register_user(async_client: AsyncClient):
    """Тестируем роутер для регистрации пользователей."""

    response = await async_client.post('/api/v1/users', json={
        "street": "Ленина",
        "house_number": "string",
        "phone_number": "+79999999999",
        "name": "string",
        "surname": "string",
        "password": "string"
    })

    assert response.status_code == 201
    assert response.json() == {
        "phone_number": "+79999999999",
        "name": "string",
        "surname": "string",
        "id": 1
    }


@pytest.mark.asyncio(scope='session')
async def test_error_register_user(async_client: AsyncClient):
    """Тестируем ошибку при регистрации пользователей с некорректным номером."""

    response = await async_client.post('/api/v1/users', json={
        "street": "Ленина",
        "house_number": "string",
        "phone_number": "string",
        "name": "string",
        "surname": "string",
        "password": "string"
    })

    assert response.status_code == 400
    assert response.json() == {'detail': 'Неверный формат номера телефона.'}


@pytest.mark.asyncio(scope='session')
async def test_login_for_user_access_token(async_client: AsyncClient):
    """Тестируем роутер для авторизации пользователей. Возвращаем токен тестового пользователя."""

    response = await async_client.post('/api/v1/users/token', json={
        "phone_number": "+79999999999",
        "password": "string"
    })

    assert response.status_code == 200

    token = response.json().get('access_token')
    assert token is not None
    return token


@pytest.mark.asyncio(scope='session')
async def test_error_login_for_user_access_token(async_client: AsyncClient):
    """Тестируем ошибку при авторизации пользователей с неверными данными."""

    response = await async_client.post('/api/v1/users/token', json={
        "phone_number": "+79999999999",
        "password": "error"
    })

    assert response.status_code == 401
    assert response.json() == {'detail': 'Неверный номер телефона или пароль.'}


@pytest.mark.asyncio(scope='session')
async def test_register_couriers(async_client: AsyncClient):
    """Тестируем роутер для регистрации курьеров."""

    response = await async_client.post('/api/v1/couriers', json={
        "phone_number": "+79999999992",
        "name": "string",
        "surname": "string",
        "password": "string"
    })

    assert response.status_code == 201
    assert response.json() == {
        "phone_number": "+79999999992",
        "name": "string",
        "surname": "string",
        "id": 1
    }


@pytest.mark.asyncio(scope='session')
async def test_error_register_couriers(async_client: AsyncClient):
    """Тестируем ошибку при регистрации курьеров с некорректным номером."""

    response = await async_client.post('/api/v1/couriers', json={
        "phone_number": "string",
        "name": "string",
        "surname": "string",
        "password": "string"
    })

    assert response.status_code == 400
    assert response.json() == {'detail': 'Неверный формат номера телефона.'}


@pytest.mark.asyncio(scope='session')
async def test_login_for_courier_access_token(async_client: AsyncClient):
    """Тестируем роутер для авторизации курьеров. Возвращаем токен тестового курьера."""

    response = await async_client.post('/api/v1/couriers/token', json={
        "phone_number": "+79999999992",
        "password": "string"
    })

    assert response.status_code == 200

    token = response.json().get('access_token')
    assert token is not None
    return token


@pytest.mark.asyncio(scope='session')
async def test_error_login_for_courier_access_token(async_client: AsyncClient):
    """Тестируем ошибку при авторизации курьеров с неверными данными."""

    response = await async_client.post('/api/v1/couriers/token', json={
        "phone_number": "+79999999992",
        "password": "error"
    })

    assert response.status_code == 401
    assert response.json() == {'detail': 'Неверный номер телефона или пароль.'}


@pytest.mark.asyncio(scope='session')
async def test_add_restaurants():
    """Создаём тестовый ресторан."""

    async with async_session_maker() as session:
        stmt = insert(Restaurant).values(
            id=7,
            name="Burgers",
            opening_time=datetime.strptime("09:15:22", "%H:%M:%S"),
            closing_time=datetime.strptime("23:15:22", "%H:%M:%S"),
            duration_delivery=50,
            city="Тюмень",
            street="Ватутина",
            house_number="14в"
        )
        await session.execute(stmt)
        await session.commit()

        result = await session.execute(select(Restaurant).filter(Restaurant.id == 7))
        assert result.scalar() is not None, "Ресторан не добавился"


@pytest.mark.asyncio(scope='session')
async def test_add_order():
    """Создаём тестовый заказ."""

    async with async_session_maker() as session:
        stmt = insert(Order).values(
            id=7,
            status="Поиск курьера",
            start_time=datetime.strptime('2024-01-06-16:22:31', "%Y-%m-%d-%H:%M:%S"),
            restaurant_id=7,
            user_id=1
        )
        await session.execute(stmt)
        await session.commit()

        result = await session.execute(select(Order).filter(Order.id == 7))
        assert result.scalar() is not None, "Заказ не добавился"

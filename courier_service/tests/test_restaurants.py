import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(scope='session')
async def test_create_restaurant(async_client: AsyncClient):
    """Тестируем роутер для регистрации нового ресторана."""

    response = await async_client.post('/api/v1/restaurants', json={
        "city": "Тюмень",
        "street": "Ленина",
        "house_number": "string",
        "name": "Pizza",
        "opening_time": "07:15:22",
        "closing_time": "23:15:22",
        "duration_delivery": 30
    })

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "name": "Pizza"
    }


@pytest.mark.asyncio(scope='session')
async def test_error_create_restaurant(async_client: AsyncClient):
    """Тестируем ошибку при регистрации нового ресторана с уже существующим названием."""

    response = await async_client.post('/api/v1/restaurants', json={
        "city": "Волгоград",
        "street": "Сибирская",
        "house_number": "74а",
        "name": "Pizza",
        "opening_time": "11:15:22",
        "closing_time": "23:15:22",
        "duration_delivery": 120
    })

    assert response.status_code == 400
    assert response.json() == {'detail': 'Такое название ресторана уже существует.'}


@pytest.mark.asyncio(scope='session')
async def test_get_restaurant_orders(async_client: AsyncClient):
    """Тестируем роутер для получения всех заказов ресторана."""

    response = await async_client.get('/api/v1/restaurants/7/orders')

    assert response.status_code == 200


@pytest.mark.asyncio(scope='session')
async def test_error_get_restaurant_orders(async_client: AsyncClient):
    """Тестируем ошибку при получении всех заказов из несуществующего ресторана."""

    response = await async_client.get('/api/v1/restaurants/17/orders')

    assert response.status_code == 404
    assert response.json() == {'detail': 'Ресторан с таким ID не найден.'}


@pytest.mark.asyncio(scope='session')
async def test_get_restaurant_order(async_client: AsyncClient):
    """Тестируем роутер для получения подробной информации о заказе для ресторана."""

    response = await async_client.get('/api/v1/restaurants/7/orders/7')

    assert response.status_code == 200


@pytest.mark.asyncio(scope='session')
async def test_error_get_restaurant_order(async_client: AsyncClient):
    """Тестируем ошибку при получении подробной информации о заказе из несуществующего ресторана."""

    response = await async_client.get('/api/v1/restaurants/17/orders/1')

    assert response.status_code == 404
    assert response.json() == {'detail': 'Заказ с такими значениями «restaurant_id» и «order_id» не найден.'}

import pytest
from httpx import AsyncClient

from .test_auth import test_login_for_courier_access_token


@pytest.mark.asyncio(scope='session')
async def test_available_couriers_orders(async_client: AsyncClient):
    """Тестируем роутер для получения списка свободных заказов для курьеров."""

    token = await test_login_for_courier_access_token(async_client)
    response = await async_client.get('/api/v1/couriers/available_orders',
                                      headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200


@pytest.mark.asyncio(scope='session')
async def test_courier_orders(async_client: AsyncClient):
    """Тестируем роутер для получения всех заказов курьера."""

    token = await test_login_for_courier_access_token(async_client)
    response = await async_client.get('/api/v1/couriers/orders',
                                      headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200


@pytest.mark.asyncio(scope='session')
async def test_error_courier_orders(async_client: AsyncClient):
    """Тестируем ошибку при получении всех заказов курьера без авторизации."""

    response = await async_client.get('/api/v1/couriers/orders')

    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}


@pytest.mark.asyncio(scope='session')
async def test_error_courier_accepts_order(async_client: AsyncClient):
    """Тестируем ошибку при попытке взять несуществующий/не активный заказ в работу."""

    token = await test_login_for_courier_access_token(async_client)
    response = await async_client.post('/api/v1/couriers/orders/17',
                                       headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 404
    assert response.json() == {'detail': 'Заказ с таким ID не найден.'}


@pytest.mark.asyncio(scope='session')
async def test_courier_accepts_order(async_client: AsyncClient):
    """Тестируем роутер для взятия заказа в работу."""

    token = await test_login_for_courier_access_token(async_client)
    response = await async_client.post('/api/v1/couriers/orders/7',
                                       headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 204


@pytest.mark.asyncio(scope='session')
async def test_courier_completes_order(async_client: AsyncClient):
    """Тестируем роутер для завершения заказа."""

    token = await test_login_for_courier_access_token(async_client)
    response = await async_client.put('/api/v1/couriers/orders/7',
                                      headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 204

import pytest
from httpx import AsyncClient

from .test_auth import test_login_for_user_access_token


@pytest.mark.asyncio(scope='session')
async def test_new_order(async_client: AsyncClient):
    """Тестируем роутер для создания заказа из ресторана."""

    token = await test_login_for_user_access_token(async_client)
    response = await async_client.post('/api/v1/users/orders/post/7',
                                       headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 201


@pytest.mark.asyncio(scope='session')
async def test_error_new_order(async_client: AsyncClient):
    """Тестируем ошибку при создании заказа из несуществующего ресторана."""

    token = await test_login_for_user_access_token(async_client)
    response = await async_client.post('/api/v1/users/orders/post/17',
                                       headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 404
    assert response.json() == {'detail': 'Нельзя сделать заказ. Ресторан с таким ID не найден.'}


@pytest.mark.asyncio(scope='session')
async def test_get_user_orders(async_client: AsyncClient):
    """Тестируем роутер для получения всех заказов пользователя."""

    token = await test_login_for_user_access_token(async_client)
    response = await async_client.get('/api/v1/users/orders/get',
                                      headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200


@pytest.mark.asyncio(scope='session')
async def test_error_get_user_orders(async_client: AsyncClient):
    """Тестируем ошибку при получении всех заказов пользователя без авторизации."""

    response = await async_client.get('/api/v1/users/orders/get')

    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}


@pytest.mark.asyncio(scope='session')
async def test_get_user_order(async_client: AsyncClient):
    """Тестируем роутер для получения подробной информации об одном заказе для пользователя."""

    token = await test_login_for_user_access_token(async_client)
    response = await async_client.get('/api/v1/users/orders/get/7',
                                      headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200


@pytest.mark.asyncio(scope='session')
async def test_error_get_user_order(async_client: AsyncClient):
    """Тестируем ошибку при получении подробной информации о несуществующем заказе для пользователя."""

    token = await test_login_for_user_access_token(async_client)
    response = await async_client.get('/api/v1/users/orders/get/17',
                                      headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 404
    assert response.json() == {'detail': 'В вашем списке заказов нет заказа с таким значением «order_id».'}


@pytest.mark.asyncio(scope='session')
async def test_shipping_cost(async_client: AsyncClient):
    """Тестируем роутер для получения стоимости доставки из выбранного ресторана."""

    token = await test_login_for_user_access_token(async_client)
    response = await async_client.get('/api/v1/users/shipping_cost/1',
                                      headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200

    # фиксированная цена доставки, если улица пользователя и ресторана одинаковая
    assert response.json() == {'shipping_cost': 50}


@pytest.mark.asyncio(scope='session')
async def test_error_shipping_cost(async_client: AsyncClient):
    """Тестируем ошибку при получении стоимости доставки из несуществующего ресторана."""

    token = await test_login_for_user_access_token(async_client)
    response = await async_client.get('/api/v1/users/shipping_cost/17',
                                      headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 404
    assert response.json() == {'detail': 'Ресторан с таким ID не найден.'}

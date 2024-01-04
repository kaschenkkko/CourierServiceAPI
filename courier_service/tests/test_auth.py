import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(scope='session')
async def test_register_user(async_client: AsyncClient):
    response = await async_client.post('/api/v1/users', json={
        "street": "string",
        "house_number": "string",
        "phone_number": "+79962100964",
        "name": "string",
        "surname": "string",
        "password": "string"
    })

    assert response.status_code == 201
    assert response.json() == {
        "phone_number": "+79962100964",
        "name": "string",
        "surname": "string",
        "id": 1
    }


@pytest.mark.asyncio(scope='session')
async def test_login_for_user_access_token(async_client: AsyncClient):
    response = await async_client.post('/api/v1/users/token', json={
        "phone_number": "+79962100964",
        "password": "string"
    })

    assert response.status_code == 200

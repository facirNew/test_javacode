from unittest.mock import AsyncMock

import pytest
from backend.app import app
from backend.database import get_session
from backend.v1.routers.wallets import get_redis
from starlette.testclient import TestClient


@pytest.mark.asyncio
async def test_get_balance_right_wallet(mock_async_session_maker: AsyncMock, mock_redis: AsyncMock):
    wallet_data = {'uuid': '123e4567-e89b-12d3-a456-426614174000', 'balance': 1000}
    mock_redis.set_mock_data(None)
    app.dependency_overrides[get_redis] = lambda: mock_redis
    app.dependency_overrides[get_session] = mock_async_session_maker(wallet_data)
    with TestClient(app) as client:
        response = client.get('/api/v1/wallets/123e4567-e89b-12d3-a456-426614174000')
    assert response.status_code == 200
    assert response.json() == {'uuid': '123e4567-e89b-12d3-a456-426614174000', 'balance': 1000.0}


@pytest.mark.asyncio
async def test_get_balance_wrong_wallet(mock_async_session_maker: AsyncMock, mock_redis: AsyncMock):
    wallet_data = {'uuid': '123e4567-e89b-12d3-a456-426614174000', 'balance': 1000}
    mock_redis.set_mock_data(None)
    app.dependency_overrides[get_redis] = lambda: mock_redis
    app.dependency_overrides[get_session] = mock_async_session_maker(wallet_data)
    with TestClient(app) as client:
        response = client.get('/api/v1/wallets/123e4567')
    assert response.status_code == 400
    assert response.json() == {'message': 'Invalid wallet UUID'}


@pytest.mark.asyncio
async def test_get_balance_right_wallet_not_found(mock_async_session_maker: AsyncMock, mock_redis: AsyncMock):
    mock_redis.set_mock_data(None)
    app.dependency_overrides[get_redis] = lambda: mock_redis
    app.dependency_overrides[get_session] = mock_async_session_maker(None)
    with TestClient(app) as client:
        response = client.get('/api/v1/wallets/123e4567-e89b-12d3-a456-426614174001')
    assert response.status_code == 404
    assert response.json() == {'message': 'Wallet not found'}


@pytest.mark.asyncio
async def test_get_balance_right_wallet_cached(mock_async_session_maker: AsyncMock, mock_redis: AsyncMock):
    mock_redis.set_mock_data({'123e4567-e89b-12d3-a456-426614174000': 1000})
    app.dependency_overrides[get_redis] = lambda: mock_redis
    app.dependency_overrides[get_session] = mock_async_session_maker(None)
    with TestClient(app) as client:
        response = client.get('/api/v1/wallets/123e4567-e89b-12d3-a456-426614174000')
    assert response.status_code == 200
    assert response.json() == {'uuid': '123e4567-e89b-12d3-a456-426614174000', 'balance': 1000.0}
    mock_redis.get.assert_called_with('123e4567-e89b-12d3-a456-426614174000')


@pytest.mark.asyncio
async def test_wallet_operation_right_wallet_right_json_deposit(
        mock_async_session_maker: AsyncMock,
        mock_redis: AsyncMock,
):
    wallet_data = {'uuid': '123e4567-e89b-12d3-a456-426614174000', 'balance': 1000}
    request_data = {'operationType': 'DEPOSIT', 'amount': 1000}
    mock_redis.set_mock_data(None)
    app.dependency_overrides[get_redis] = lambda: mock_redis
    app.dependency_overrides[get_session] = mock_async_session_maker(wallet_data)
    with TestClient(app) as client:
        response = client.post(
            '/api/v1/wallets/123e4567-e89b-12d3-a456-426614174000/operation',
            json=request_data,
        )
    assert response.status_code == 200
    assert response.json() == {'message': 'Operation succeeded'}
    mock_redis.set.assert_called_with('123e4567-e89b-12d3-a456-426614174000', 2000.0, ex=3600)


@pytest.mark.asyncio
async def test_wallet_operation_right_wallet_right_json_withdraw(
        mock_async_session_maker: AsyncMock,
        mock_redis: AsyncMock,
):
    wallet_data = {'uuid': '123e4567-e89b-12d3-a456-426614174000', 'balance': 1000}
    request_data = {'operationType': 'WITHDRAW', 'amount': 1000}
    mock_redis.set_mock_data(None)
    app.dependency_overrides[get_redis] = lambda: mock_redis
    app.dependency_overrides[get_session] = mock_async_session_maker(wallet_data)
    with TestClient(app) as client:
        response = client.post(
            '/api/v1/wallets/123e4567-e89b-12d3-a456-426614174000/operation',
            json=request_data,
        )
    assert response.status_code == 200
    assert response.json() == {'message': 'Operation succeeded'}
    mock_redis.set.assert_called_with('123e4567-e89b-12d3-a456-426614174000', 0.0, ex=3600)


@pytest.mark.asyncio
async def test_wallet_operation_right_wallet_right_json_negative_withdraw(
        mock_async_session_maker: AsyncMock,
        mock_redis: AsyncMock,
):
    wallet_data = {'uuid': '123e4567-e89b-12d3-a456-426614174000', 'balance': 1000}
    request_data = {'operationType': 'WITHDRAW', 'amount': 1001}
    mock_redis.set_mock_data(None)
    app.dependency_overrides[get_redis] = lambda: mock_redis
    app.dependency_overrides[get_session] = mock_async_session_maker(wallet_data)
    with TestClient(app) as client:
        response = client.post(
            '/api/v1/wallets/123e4567-e89b-12d3-a456-426614174000/operation',
            json=request_data,
        )
    assert response.status_code == 400
    assert response.json() == {'message': 'Not enough balance'}
    mock_redis.set.assert_not_called()


@pytest.mark.parametrize('request_data',
                         [
                             {'operationType': '', 'amount': 1000},
                             {'operationType': 'Some text', 'amount': 1000},
                             {'operationType': 'DEPOSIT', 'amount': -1000},
                             {'operationType': 'WITHDRAW', 'amount': -1000},
                             {'operationType': 'DEPOSIT', 'amount': 0},
                             {'operationType': 'WITHDRAW'},
                             {'amount': 1000},
                         ],
                         )
@pytest.mark.asyncio
async def test_wallet_operation_right_wallet_wrong_json(
        mock_async_session_maker: AsyncMock,
        mock_redis: AsyncMock,
        request_data: dict,
):
    wallet_data = {'uuid': '123e4567-e89b-12d3-a456-426614174000', 'balance': 1000}
    mock_redis.set_mock_data(None)
    app.dependency_overrides[get_redis] = lambda: mock_redis
    app.dependency_overrides[get_session] = mock_async_session_maker(wallet_data)
    with TestClient(app) as client:
        response = client.post(
            '/api/v1/wallets/123e4567-e89b-12d3-a456-426614174000/operation',
            json=request_data,
        )
    assert response.status_code == 422
    assert response.json() == {'message': 'JSON validation failed'}


@pytest.mark.parametrize(
    'wallet_string',
    [
        'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'a',
        '12345',
        '123e4567-e89b-12d3-a456-426614174000-123e4567-e89b-12d3-a456-426614174000',
    ],
)
@pytest.mark.asyncio
async def test_wallet_operation_wrong_wallet(
        mock_async_session_maker: AsyncMock,
        mock_redis: AsyncMock,
        wallet_string: str,
):
    wallet_data = {'uuid': '123e4567-e89b-12d3-a456-426614174000', 'balance': 1000}
    request_data = {'operationType': 'DEPOSIT', 'amount': 1000}
    mock_redis.set_mock_data(None)
    app.dependency_overrides[get_redis] = lambda: mock_redis
    app.dependency_overrides[get_session] = mock_async_session_maker(wallet_data)
    with TestClient(app) as client:
        response = client.post(
            f'/api/v1/wallets/{wallet_string}/operation',
            json=request_data,
        )
    assert response.status_code == 400
    assert response.json() == {'message': 'Invalid wallet UUID'}

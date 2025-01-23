from unittest.mock import AsyncMock

import pytest
from backend.v1.models import Wallet


@pytest.fixture(scope='function')
def mock_async_session_maker():
    def factory(wallet_data=None):
        class MockResult:
            def scalar_one_or_none(self):
                return Wallet(**wallet_data) if wallet_data else None

        class MockSession:
            async def execute(self, query):
                return MockResult()

            async def commit(self):
                return None

            async def rollback(self):
                return None

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        async def session_maker():
            return MockSession()

        return session_maker
    return factory


@pytest.fixture(scope='function')
def mock_redis():
    redis_mock = AsyncMock()
    def set_mock_data(data_dict: dict | None = None):
        if data_dict is None:
            data_dict = {}
        redis_mock.get.side_effect = lambda key: data_dict.get(key, None)

    redis_mock.set.return_value = None
    redis_mock.set_mock_data = set_mock_data
    return redis_mock

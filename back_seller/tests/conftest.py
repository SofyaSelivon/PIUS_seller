import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def db():
    return AsyncMock()
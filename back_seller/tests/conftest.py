from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def db():
    return AsyncMock()

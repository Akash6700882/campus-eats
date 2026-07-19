from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.core.deps import require_role

pytestmark = pytest.mark.asyncio


def _user_with_role(role_name: str):
    return SimpleNamespace(role=SimpleNamespace(name=role_name))


async def test_require_role_allows_matching_role():
    dependency = require_role("kitchen")
    user = _user_with_role("kitchen")
    result = await dependency(user)
    assert result is user


async def test_require_role_blocks_non_matching_role():
    dependency = require_role("kitchen")
    user = _user_with_role("customer")
    with pytest.raises(HTTPException) as exc_info:
        await dependency(user)
    assert exc_info.value.status_code == 403


async def test_require_role_allows_any_of_multiple_roles():
    dependency = require_role("admin", "kitchen")
    user = _user_with_role("kitchen")
    result = await dependency(user)
    assert result is user

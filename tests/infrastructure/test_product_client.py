"""商品服務 HTTP 客戶端測試。"""

import httpx
import pytest

from domain.order import ProductNotFoundError, ProductReference, ProductUnavailableError
from infrastructure.product_client import ProductClient


def make_client(status: int = 200, json_body: dict | None = None, fail_with=None) -> ProductClient:
    def handler(request: httpx.Request) -> httpx.Response:
        if fail_with is not None:
            raise fail_with
        return httpx.Response(status, json=json_body or {"detail": ""})

    return ProductClient("http://faked", transport=httpx.MockTransport(handler))


async def test_get_product_maps_200_to_reference() -> None:
    """情境：上游 200 → 字段正確映射為 ProductReference。"""
    client = make_client(200, {"product_id": "p-1", "name": "鍵盤", "price": 350})

    result = await client.get_product("p-1")

    assert result == ProductReference("p-1", "鍵盤", 350)


async def test_get_product_404_raises_product_not_found() -> None:
    """情境：上游 404 → ProductNotFoundError。"""
    client = make_client(404)

    with pytest.raises(ProductNotFoundError):
        await client.get_product("p-x")


async def test_get_product_500_raises_product_unavailable() -> None:
    """情境：上游 500 → ProductUnavailableError。"""
    client = make_client(500)

    with pytest.raises(ProductUnavailableError):
        await client.get_product("p-1")


async def test_connect_error_raises_product_unavailable() -> None:
    """情境：network 不可達 → ProductUnavailableError。"""
    client = make_client(fail_with=httpx.ConnectError("connection refused"))

    with pytest.raises(ProductUnavailableError):
        await client.get_product("p-1")

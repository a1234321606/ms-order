"""訂單服務 API 層測試。"""

import httpx
import pytest

from interfaces.api import create_app
from main import app as main_built_app


@pytest.fixture
async def app_client(fake_product_client, order_repository):
    """建立測試用的 API 客戶端。"""
    transport = httpx.ASGITransport(app=create_app(product_client=fake_product_client, repository=order_repository))
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def main_app():
    """取得 main.py 組裝的應用。"""
    return main_built_app


@pytest.fixture
async def created_order(app_client):
    """建立一筆測試用訂單。"""
    response = await app_client.post(
        "/orders",
        json={"customer_name": "Alice", "lines": [{"product_id": "p-1", "quantity": 2}]},
    )
    return response.json()


async def test_healthz(app_client) -> None:
    """情境：服務存活。"""
    response = await app_client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_create_order_201_priced_by_service(app_client) -> None:
    """情境：建立合法訂單 → 201；金額以商品服務的價格計算。"""
    response = await app_client.post(
        "/orders",
        json={
            "customer_name": "Alice",
            "lines": [{"product_id": "p-1", "quantity": 2}, {"product_id": "p-2", "quantity": 1}],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["total"] == 2 * 350 + 129
    assert body["order_id"].startswith("o-")
    assert len(body["lines"]) == 2
    assert all("unit_price" in line for line in body["lines"])


async def test_create_order_404_unknown_product(app_client) -> None:
    """情境：商品不存在(上游 404)→ 404。"""
    response = await app_client.post(
        "/orders", json={"customer_name": "Alice", "lines": [{"product_id": "p-x", "quantity": 1}]}
    )

    assert response.status_code == 404


async def test_create_order_400_zero_quantity(app_client) -> None:
    """情境：訂單物品數量為 0 → 400。"""
    response = await app_client.post(
        "/orders", json={"customer_name": "Alice", "lines": [{"product_id": "p-1", "quantity": 0}]}
    )

    assert response.status_code == 400


async def test_create_order_502_product_client_down(failing_product_client, order_repository) -> None:
    """情境：商品服務不可達 → 502 Bad Gateway。"""
    transport = httpx.ASGITransport(app=create_app(product_client=failing_product_client, repository=order_repository))
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/orders", json={"customer_name": "Alice", "lines": [{"product_id": "p-1", "quantity": 1}]}
        )

    assert response.status_code == 502


async def test_create_order_fetches_each_line_once(app_client, fake_product_client) -> None:
    """情境：建立訂單時，向商品服務查詢每一行的價格。"""
    await app_client.post("/orders", json={"customer_name": "Carol", "lines": [{"product_id": "p-2", "quantity": 1}]})

    assert fake_product_client.calls == ["p-2"]


async def test_get_order_200_saved(app_client, created_order) -> None:
    """情境：取回已建立的訂單，內容與存檔一致。"""
    response = await app_client.get(f"/orders/{created_order['order_id']}")

    assert response.status_code == 200
    assert response.json() == created_order


async def test_get_order_404_unknown_id(app_client) -> None:
    """情境：取回不存在的訂單 → 404。"""
    response = await app_client.get("/orders/o-nope")

    assert response.status_code == 404


async def test_list_orders_200_lists_saved(app_client, created_order) -> None:
    """情境：列出所有訂單 → 只含已建立的那一筆。"""
    response = await app_client.get("/orders")

    assert response.status_code == 200
    assert [item["order_id"] for item in response.json()] == [created_order["order_id"]]


async def test_main_entrypoint_smoke(main_app) -> None:
    """情境：main.py 組裝的 app 可通過健康檢查。"""
    transport = httpx.ASGITransport(app=main_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/healthz")

    assert response.status_code == 200

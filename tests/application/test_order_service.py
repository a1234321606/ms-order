"""訂單服務的單元測試"""

import pytest

from application.order_service import OrderService
from domain.order import InvalidQuantityError, OrderNotFoundError, ProductNotFoundError, ProductUnavailableError
from infrastructure.order_repository import OrderRepository


@pytest.fixture
def repository(tmp_path) -> OrderRepository:
    return OrderRepository(str(tmp_path / "orders.db"))


def make_service(product_client, repository) -> OrderService:
    return OrderService(product_client=product_client, repository=repository)


async def test_create_order_happy_path_uses_service_prices(fake_product_client, repository) -> None:
    """情境：合法兩行 → 建立成功，金額採用商品服務的價格。"""
    service = make_service(fake_product_client, repository)

    order = await service.create_order("Alice", [("p-1", 2), ("p-2", 1)])
    fetched = await service.get_order(order.order_id)
    listed = await service.list_orders()

    assert fetched.lines[0].unit_price == 350
    assert fetched.total == 2 * 350 + 129
    assert listed == [order]


async def test_create_order_missing_product_raises_product_not_found(fake_product_client, repository) -> None:
    """情境：商品服務說商品不存在 → ProductNotFoundError 上拋。"""
    service = make_service(fake_product_client, repository)

    with pytest.raises(ProductNotFoundError):
        await service.create_order("Alice", [("p-missing", 1)])


async def test_create_order_zero_quantity_raises_invalid_quantity(fake_product_client, repository) -> None:
    """情境：quantity 0 → InvalidQuantityError。"""
    service = make_service(fake_product_client, repository)

    with pytest.raises(InvalidQuantityError):
        await service.create_order("Alice", [("p-1", 0)])


async def test_get_unknown_order_raises_order_not_found(fake_product_client, repository) -> None:
    """情境：不存在的訂單 → OrderNotFoundError。"""
    service = make_service(fake_product_client, repository)

    with pytest.raises(OrderNotFoundError):
        await service.get_order("o-missing")


async def test_product_client_down_raises_product_unavailable(failing_product_client, repository) -> None:
    """情境：商品服務不可達 → ProductUnavailableError。"""
    service = make_service(failing_product_client, repository)

    with pytest.raises(ProductUnavailableError):
        await service.create_order("Alice", [("p-1", 1)])

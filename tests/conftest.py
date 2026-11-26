"""共用 fixtures
外部服務使用Mock替代，避免影響測試。
"""

import pytest

from domain.order import ProductNotFoundError, ProductReference, ProductUnavailableError
from infrastructure.order_repository import OrderRepository


class FakeProductClient:
    """假商品服務：外部 ms-product 的替身。"""

    def __init__(self) -> None:
        self._products = {
            "p-1": ProductReference("p-1", "機械式鍵盤", 350),
            "p-2": ProductReference("p-2", "無線滑鼠", 129),
        }
        self.calls: list[str] = []

    async def get_product(self, product_id: str) -> ProductReference:
        self.calls.append(product_id)
        if product_id not in self._products:
            raise ProductNotFoundError(product_id)
        return self._products[product_id]


class FailingProductClient:
    """假商品服務：模擬商品服務整個掛掉。"""

    async def get_product(self, product_id: str) -> ProductReference:
        raise ProductUnavailableError("connection refused")


@pytest.fixture
def fake_product_client() -> FakeProductClient:
    """給一份含已知商品 p-1/p-2 的假商品服務。"""
    return FakeProductClient()


@pytest.fixture
def failing_product_client() -> FailingProductClient:
    """給一份永遠失敗的假商品服務。"""
    return FailingProductClient()


@pytest.fixture
def order_repository(tmp_path) -> OrderRepository:
    """測試用的訂單存儲。"""
    return OrderRepository(str(tmp_path / "orders.db"))

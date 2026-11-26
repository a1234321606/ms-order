"""訂單模型。"""

from dataclasses import dataclass, field
from datetime import UTC, datetime


class InvalidQuantityError(Exception):
    """訂單項目數量小於 1。"""


@dataclass(frozen=True)
class OrderLine:
    """訂單物品。

    Args:
        product_id: 商品 ID。
        quantity: 購買數量(≥ 1)。
        unit_price: 單價，由商品服務取得。
    """

    product_id: str
    quantity: int
    unit_price: int

    def __post_init__(self) -> None:
        if self.quantity < 1:
            raise InvalidQuantityError(f"quantity 必須 ≥ 1，收到 {self.quantity}")

    @property
    def line_total(self) -> int:
        """訂單物品總價。"""
        return self.quantity * self.unit_price


@dataclass(frozen=True)
class Order:
    """訂單。

    Args:
        order_id: 訂單 ID(系統生成)。
        customer_name: 顧客名稱。
        lines: 訂單物品。
        created_at: 建立時間(UTC)。
    """

    order_id: str
    customer_name: str
    lines: list[OrderLine] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def total(self) -> int:
        """訂單總價。"""
        return sum(line.line_total for line in self.lines)


@dataclass(frozen=True)
class ProductReference:
    """訂單的商品參考。不複製 ms-product 的完整模型，只保留訂單服務關心的字段。

    Args:
        product_id: 商品 ID。
        name: 商品名稱。
        price: 單價，取自商品服務。
    """

    product_id: str
    name: str
    price: int


class ProductNotFoundError(Exception):
    """商品服務回傳 404：該商品不存在。"""


class ProductUnavailableError(Exception):
    """商品服務不可達，或回傳 5xx／其他非 404 錯誤。"""


class OrderNotFoundError(Exception):
    """訂單不存在。"""

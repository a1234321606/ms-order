"""API 請求／回應 模型。"""

from pydantic import BaseModel

from domain.order import Order


class OrderLineIn(BaseModel):
    """訂單物品請求。

    Fields:
        product_id: 商品 ID。
        quantity: 購買數量。
    """

    product_id: str
    quantity: int


class CreateOrderRequest(BaseModel):
    """建立訂單請求。

    Fields:
        customer_name: 顧客名稱。
        lines: 訂單物品。
    """

    customer_name: str
    lines: list[OrderLineIn]


class OrderLineOut(BaseModel):
    """訂單物品回應。

    Fields:
        product_id: 商品 ID。
        quantity: 數量。
        unit_price: 單價。
        line_total: 物品總價。
    """

    product_id: str
    quantity: int
    unit_price: int
    line_total: int


class OrderOut(BaseModel):
    """訂單回應模型。

    Fields:
        order_id: 訂單 ID。
        customer_name: 顧客名稱。
        total: 訂單總價。
        lines: 訂單物品。
    """

    order_id: str
    customer_name: str
    total: int
    lines: list[OrderLineOut]

    @classmethod
    def from_domain(cls, order: Order) -> "OrderOut":
        """將訂單的業務模型轉換為回應模型。"""
        return cls(
            order_id=order.order_id,
            customer_name=order.customer_name,
            total=order.total,
            lines=[
                OrderLineOut(
                    product_id=line.product_id,
                    quantity=line.quantity,
                    unit_price=line.unit_price,
                    line_total=line.line_total,
                )
                for line in order.lines
            ],
        )

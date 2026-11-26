"""訂單業務邏輯。"""

from uuid import uuid4

from domain.order import Order, OrderLine


class OrderService:
    """訂單業務邏輯。

    Args:
        product_client: 商品查詢物件。
        repository: 訂單存儲物件。
    """

    def __init__(self, product_client, repository) -> None:
        self._product_client = product_client
        self._repository = repository

    async def create_order(self, customer_name: str, items: list[tuple[str, int]]) -> Order:
        """建立訂單；逐項向商品服務取價。

        Args:
            customer_name: 顧客名稱。
            items: (product_id, quantity) 清單。

        Returns:
            已儲存的訂單。
        """
        lines = [await self._build_line(product_id, quantity) for product_id, quantity in items]
        order = Order(order_id=f"o-{uuid4().hex[:8]}", customer_name=customer_name, lines=lines)
        await self._repository.save(order)
        return order

    async def get_order(self, order_id: str) -> Order:
        """取回單一訂單。

        Args:
            order_id: 訂單 ID。

        Returns:
            對應的訂單。

        Raises:
            OrderNotFoundError: 訂單不存在。
        """
        return await self._repository.get(order_id)

    async def list_orders(self) -> list[Order]:
        """列出全部訂單。"""
        return await self._repository.list_all()

    async def _build_line(self, product_id: str, quantity: int) -> OrderLine:
        product = await self._product_client.get_product(product_id)
        return OrderLine(product_id=product.product_id, quantity=quantity, unit_price=product.price)

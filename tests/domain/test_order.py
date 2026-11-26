"""訂單模型測試。"""

import pytest

from domain.order import InvalidQuantityError, Order, OrderLine


def test_order_totals_happy_path() -> None:
    """情境：訂單有兩行 → 總價正確計算。"""
    order = Order(
        order_id="o-001",
        customer_name="Alice",
        lines=[OrderLine("p-1", 2, 1000), OrderLine("p-2", 1, 300)],
    )

    assert order.total == 2300
    assert order.customer_name == "Alice"


def test_order_with_no_lines_has_zero_total() -> None:
    """情境：訂單沒有物品 → 總價為 0。"""
    order = Order(order_id="o-002", customer_name="Bob")

    assert order.total == 0


@pytest.mark.parametrize("quantity", [0, -3])
def test_order_line_rejects_zero_or_negative_quantity(quantity: int) -> None:
    """情境：訂單物品數量為 0 或負數 → InvalidQuantityError。"""
    with pytest.raises(InvalidQuantityError):
        OrderLine("p-1", quantity, 100)

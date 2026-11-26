"""訂單存儲。"""

from datetime import datetime

import aiosqlite

from domain.order import Order, OrderLine, OrderNotFoundError

_SCHEMA_ORDERS = """
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""

_SCHEMA_LINES = """
CREATE TABLE IF NOT EXISTS order_lines (
    order_id TEXT NOT NULL,
    seq INTEGER NOT NULL,
    product_id TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price INTEGER NOT NULL,
    PRIMARY KEY (order_id, seq)
);
"""


class OrderRepository:
    """DB的訂單存儲。"""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    async def _connect(self) -> aiosqlite.Connection:
        """開啟連線並確保表存在；呼叫端負責 close。"""
        db = await aiosqlite.connect(self._db_path)
        await db.execute(_SCHEMA_ORDERS)
        await db.execute(_SCHEMA_LINES)
        return db

    async def save(self, order: Order) -> None:
        db = await self._connect()
        try:
            await db.execute(
                "INSERT INTO orders (order_id, customer_name, created_at) VALUES (?, ?, ?)",
                (order.order_id, order.customer_name, order.created_at.isoformat()),
            )
            for seq, line in enumerate(order.lines):
                await db.execute(
                    "INSERT INTO order_lines (order_id, seq, product_id, quantity, unit_price) VALUES (?, ?, ?, ?, ?)",
                    (order.order_id, seq, line.product_id, line.quantity, line.unit_price),
                )
            await db.commit()
        finally:
            await db.close()

    async def _load(self, db: aiosqlite.Connection, order_id: str) -> Order:
        async with db.execute(
            "SELECT order_id, customer_name, created_at FROM orders WHERE order_id = ?",
            (order_id,),
        ) as cursor:
            row = await cursor.fetchone()
        if row is None:
            raise OrderNotFoundError(f"訂單 {order_id!r} 不存在")
        async with db.execute(
            "SELECT product_id, quantity, unit_price FROM order_lines WHERE order_id = ? ORDER BY seq",
            (order_id,),
        ) as cursor:
            rows = await cursor.fetchall()
        lines = [OrderLine(product_id=r[0], quantity=r[1], unit_price=r[2]) for r in rows]
        return Order(order_id=row[0], customer_name=row[1], lines=lines, created_at=datetime.fromisoformat(row[2]))

    async def get(self, order_id: str) -> Order:
        db = await self._connect()
        try:
            return await self._load(db, order_id)
        finally:
            await db.close()

    async def list_all(self) -> list[Order]:
        db = await self._connect()
        try:
            async with db.execute("SELECT order_id FROM orders") as cursor:
                ids = [r[0] for r in await cursor.fetchall()]
            return [await self._load(db, order_id) for order_id in ids]
        finally:
            await db.close()

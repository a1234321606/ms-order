"""FastAPI 入口"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from application.order_service import OrderService
from domain.order import (
    InvalidQuantityError,
    OrderNotFoundError,
    ProductNotFoundError,
    ProductUnavailableError,
)
from interfaces.schemas import CreateOrderRequest, OrderOut


def create_app(product_client, repository) -> FastAPI:
    """組裝 ms-order FastAPI 應用。

    Args:
        product_client: 商品查詢物件。
        repository: 訂單存儲物件。

    Returns:
        配置完成的 FastAPI 實例。
    """
    order_service = OrderService(product_client=product_client, repository=repository)
    app = FastAPI(title="ms-order", version="0.1.0")

    @app.exception_handler(OrderNotFoundError)
    async def on_order_not_found(_: Request, exc: OrderNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ProductNotFoundError)
    async def on_product_not_found(_: Request, exc: ProductNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": f"商品不存在：{exc}"})

    @app.exception_handler(ProductUnavailableError)
    async def on_product_unavailable(_: Request, exc: ProductUnavailableError) -> JSONResponse:
        return JSONResponse(status_code=502, content={"detail": f"商品服務暫時不可用：{exc}"})

    @app.exception_handler(InvalidQuantityError)
    async def on_invalid_quantity(_: Request, exc: InvalidQuantityError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        """健康檢查。"""
        return {"status": "ok"}

    @app.get("/orders", response_model=list[OrderOut])
    async def list_orders() -> list[OrderOut]:
        """列出全部訂單。"""
        return [OrderOut.from_domain(order) for order in await order_service.list_orders()]

    @app.get("/orders/{order_id}", response_model=OrderOut)
    async def get_order(order_id: str) -> OrderOut:
        """依 ID 取得訂單。"""
        return OrderOut.from_domain(await order_service.get_order(order_id))

    @app.post("/orders", response_model=OrderOut, status_code=201)
    async def create_order(payload: CreateOrderRequest) -> OrderOut:
        """建立訂單。"""
        items = [(line.product_id, line.quantity) for line in payload.lines]
        order = await order_service.create_order(payload.customer_name, items)
        return OrderOut.from_domain(order)

    return app

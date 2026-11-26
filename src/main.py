"""服務入口：組裝service和repository，並啟動 FastAPI。"""

import os

import uvicorn
from fastapi import FastAPI

from infrastructure.order_repository import OrderRepository
from infrastructure.product_client import ProductClient
from interfaces.api import create_app


def build_app() -> FastAPI:
    product_client = ProductClient(os.getenv("PRODUCT_API_URL", "http://localhost:8001"))
    db_path = os.getenv("DB_PATH", "data/orders.db")
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    repository = OrderRepository(db_path)
    return create_app(product_client=product_client, repository=repository)


app = build_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8002")))

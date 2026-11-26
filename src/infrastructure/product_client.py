"""商品服務 HTTP 客戶端。"""

import httpx

from domain.order import ProductNotFoundError, ProductReference, ProductUnavailableError


class ProductClient:
    """商品服務 HTTP 客戶端。

    Args:
        product_api_url: ms-product 的URL，compose 內為 http://ms-product:8001。
        transport: 可自訂 httpx transport。
    """

    def __init__(self, product_api_url: str, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._base_url = product_api_url.rstrip("/")
        self._client = httpx.AsyncClient(transport=transport) if transport is not None else httpx.AsyncClient()

    def close(self) -> None:
        """關閉 HTTP 連接池。"""
        self._client.close()

    async def get_product(self, product_id: str) -> ProductReference:
        """向商品服務取回商品。

        Returns:
            ProductReference。

        Raises:
            ProductNotFoundError: 上游 404。
            ProductUnavailableError: 上游不可達、5xx 或其他錯誤。
        """
        try:
            response = await self._client.get(f"{self._base_url}/products/{product_id}")
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise ProductNotFoundError(f"商品服務沒有商品 {product_id!r}") from None
            raise ProductUnavailableError(f"商品服務回傳 {exc.response.status_code}") from None
        except httpx.HTTPError as exc:
            raise ProductUnavailableError(f"無法連上商品服務：{exc}") from None
        data = response.json()
        return ProductReference(product_id=data["product_id"], name=data["name"], price=data["price"])

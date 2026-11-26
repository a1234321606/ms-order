# ms-order — 訂單微服務

[microservice 授課 POC](https://github.com/a1234321606/ms-bootstrap)(三 repo 結構)之一。
負責下單／查單。它是 [ms-product](https://github.com/a1234321606/ms-product)
的**下游**：下單時會透過 HTTP 來 ms-product 查價格。

技術棧：uv + Python 3.13 + FastAPI + httpx，DDD 分層。

## Quick start

```bash
# 建立 .venv 並安裝全部依賴(含 dev)
uv sync

# 設定VSCode自動執行`source .venv/bin/activate`
`Ctrl+Shift+P` / `Cmd+Shift+P` → search for `Python: Select Interpreter` → choose the one in this project:
Ex: `Python 3.13.5 (ms-order) ./.venv/bin/python`

# 啟動服務(port 8002；需先啟動 ms-product，或預設 PRODUCT_API_URL http://localhost:8001)
python src/main.py
```

此專案進行開發時 ms-product 需另行啟動(或用 ms-bootstrap 的 compose 啟動)。

另開一個 terminal 驗收：

```bash
# 確認服務已啟動
curl localhost:8002/healthz

# 下單，購買 2 台 id 為 p-xxxx 的商品(價格由 ms-product 查回，請求不帶價格)
curl localhost:8002/orders -H 'Content-Type: application/json' -d '{"customer_name":"Alice","lines":[{"product_id":"p-xxxx","quantity":2}]}'

# 列出訂單
curl localhost:8002/orders
```

## API

 Method | Path           | 說明
--------|----------------|------------------------------------------------------------
 GET    | `/healthz`     | 健康檢查                                                    
 GET    | `/orders`      | 列出全部訂單                                                
 GET    | `/orders/{id}` | 訂單詳情(不存在 → 404)                                      
 POST   | `/orders`      | 下單(201；商品不存在 → 404；商品服務掛 → 502；quantity<1 → 400)

## DDD 分層

```
domain/          # 業務的概念、規則定義
application/     # 完整業務邏輯
infrastructure/  # 處理外部服務，ex: DB, FS, 3rd-party API, queue, etc.
interfaces/      # 處理外部請求，即FastAPI入口
```

依賴方向：`interfaces → application / infrastructure → domain`；domain 不依賴任何人。

## 測試

```bash
# 執行所有測試
pytest

# 執行特定名稱的測試
pytest -k test_function_name
```

## Docker

```bash
# 編譯docker映像檔
docker build -t ms-order .

# 啟動docker服務
docker run --rm -p 8002:8002 ms-order
```

或直接到 [ms-bootstrap](https://github.com/a1234321606/ms-bootstrap) 用 docker compose 一鍵啟動整套。

## 相關 repo

- [ms-product](https://github.com/a1234321606/ms-product) — 上游商品目錄服務
- [ms-bootstrap](https://github.com/a1234321606/ms-bootstrap) — 課程主入口

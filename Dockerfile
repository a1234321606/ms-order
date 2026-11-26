# 指定使用Python 3.13的精簡版本
FROM python:3.13-slim

# 安裝 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# 設定容器的工作目錄
WORKDIR /app

# 複製檔案到/app，接著安裝已鎖定的套件，但不安裝開發套件
COPY pyproject.toml uv.lock .
RUN uv sync --frozen --no-dev

# 最後放程式碼，避免改程式碼就重裝依賴 (利用docker暫存加速編譯)
COPY src .

# 設定服務的埠號為8002
ENV PORT=8002

# 啟動服務(shell form：${PORT} 於容器啟動時才展開，exec 讓訊號直達 uvicorn)
CMD ["sh", "-c", "exec uv run --no-sync uvicorn main:app --host 0.0.0.0 --port ${PORT:-8002}"]

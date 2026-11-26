"""測試專案的DDD分層架構"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_layering_contracts():
    """情境：檢查 DDD 分層契約，確保 domain 層不依賴 application 與 interfaces 層。"""
    lint = Path(sys.executable).parent / "lint-imports"
    if not lint.exists():
        pytest.skip("import-linter 不在此 venv，先跑 uv sync")
    result = subprocess.run(
        [str(lint)], cwd=REPO_ROOT, env={**os.environ, "PYTHONPATH": "src"}, capture_output=True, text=True
    )
    assert result.returncode == 0, f"DDD 分層違規：\n{result.stdout}{result.stderr}"


def test_no_dead_code():
    """情境：檢查專案中是否有死碼，確保程式碼品質。"""
    vulture = Path(sys.executable).parent / "vulture"
    if not vulture.exists():
        pytest.skip("vulture 不在此 venv，先跑 uv sync")
    result = subprocess.run(
        [str(vulture), "src", "--min-confidence", "80"], cwd=REPO_ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, f"vulture 發現死碼：\n{result.stdout}{result.stderr}"

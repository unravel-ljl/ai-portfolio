import pytest
from fastapi.testclient import TestClient

import app.api.routes as routes
from app.main import app
from app.services.llm import LLMError

client = TestClient(app)


@pytest.fixture(autouse=True)
def fake_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    """本文件所有测试都用假模型，不联网。"""
    monkeypatch.setattr(routes, "ask_llm", lambda q: f"假回答：{q}")


def test_ask_returns_answer() -> None:
    resp = client.post("/ask", json={"question": "什么是 RAG"})
    assert resp.status_code == 200
    body = resp.json()
    assert "什么是 RAG" in body["answer"]
    assert isinstance(body["cost_ms"], int)


def test_ask_rejects_empty_question() -> None:
    assert client.post("/ask", json={"question": ""}).status_code == 422


def test_ask_rejects_missing_field() -> None:
    assert client.post("/ask", json={}).status_code == 422


def test_ask_rejects_too_long() -> None:
    assert client.post("/ask", json={"question": "x" * 501}).status_code == 422


def test_ask_returns_503_when_llm_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    """模型挂了要返回 503 + 人话提示，不能崩成 500。"""

    def boom(q: str) -> str:
        raise LLMError("模型服务暂时不可用")

    monkeypatch.setattr(routes, "ask_llm", boom)
    resp = client.post("/ask", json={"question": "hi"})
    assert resp.status_code == 503
    assert "暂时不可用" in resp.json()["detail"]
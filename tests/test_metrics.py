from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_metrics_increases_after_ask() -> None:
    """断言"增加 1"，而不是"等于 1"——避免被其它测试的调用污染。"""
    before = client.get("/metrics").json()["calls"]

    resp = client.post("/ask", json={"question": "hi"})
    assert resp.status_code == 200

    after = client.get("/metrics").json()["calls"]
    assert after == before + 1

from fastapi.testclient import TestClient

from apps.api.main import app


def test_chat_returns_schedule_preview() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/chat",
        json={
            "user_id": "demo-user",
            "session_id": "demo-session",
            "message": "I want to work from 9-12, gym at 6, dinner at 8",
            "mode": "preview",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "demo-session"
    assert len(data["changes"]["events"]) >= 3
    assert data["changes"]["mode"] == "preview"

import pytest
from unittest.mock import patch, MagicMock
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestAIChat:
    def test_chat_success(self, client):
        with patch("app.services.ai_service._configure_gemini"), \
             patch("app.services.ai_service.genai.GenerativeModel") as mock_model_cls, \
             patch("app.services.ai_service._load_session", return_value=[]), \
             patch("app.services.ai_service._save_session"):

            mock_response = MagicMock()
            mock_response.text = "I hear you. Let's talk more about that."
            mock_chat = MagicMock()
            mock_chat.send_message.return_value = mock_response
            mock_model_cls.return_value.start_chat.return_value = mock_chat

            resp = client.post("/api/ai/chat", json={
                "user_id": "user-uuid-1",
                "message": "I'm feeling really stressed about exams.",
            })
            assert resp.status_code == 200
            data = resp.get_json()
            assert "reply" in data
            assert "mood_score" in data
            assert "session_id" in data

    def test_chat_missing_fields(self, client):
        resp = client.post("/api/ai/chat", json={"user_id": "user-1"})
        assert resp.status_code == 400

    def test_chat_no_body(self, client):
        resp = client.post("/api/ai/chat")
        assert resp.status_code == 400

    def test_history_missing_param(self, client):
        resp = client.get("/api/ai/history")
        assert resp.status_code == 400

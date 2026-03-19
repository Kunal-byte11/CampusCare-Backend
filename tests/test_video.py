import pytest
from unittest.mock import patch
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _valid_auth_header():
    """Return a mock Authorization header (test skips real JWT validation)."""
    return {"Authorization": "Bearer fake.test.token"}


class TestVideoToken:
    def test_token_no_auth(self, client):
        resp = client.get("/api/video/token?channel=room123")
        assert resp.status_code == 401

    def test_token_missing_channel(self, client):
        with patch("app.utils.auth_guard.jwt.decode") as mock_decode:
            mock_decode.return_value = {"sub": "user-1", "app_metadata": {}}
            resp = client.get("/api/video/token", headers=_valid_auth_header())
            assert resp.status_code == 400

    def test_token_generates_successfully(self, client):
        with patch("app.utils.auth_guard.jwt.decode") as mock_decode, \
             patch("app.routes.video_call.generate_rtc_token",
                   return_value=({"token": "fake-agora-token", "channel": "room123", "uid": 42}, None)):
            mock_decode.return_value = {"sub": "user-1", "app_metadata": {}}
            resp = client.get(
                "/api/video/token?channel=room123&uid=42",
                headers=_valid_auth_header(),
            )
            assert resp.status_code == 200
            data = resp.get_json()
            assert data["token"] == "fake-agora-token"
            assert data["channel"] == "room123"

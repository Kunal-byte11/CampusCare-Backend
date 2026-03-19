import pytest
from unittest.mock import patch, MagicMock
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _mock_booking(overrides=None):
    base = {
        "id": "booking-uuid-1",
        "anonymous_id": "anon_abc123",
        "counselor_id": "counselor-uuid-1",
        "scheduled_at": "2026-04-01T10:00:00",
        "status": "pending",
        "notes": "",
    }
    if overrides:
        base.update(overrides)
    return base


class TestCreateBooking:
    def test_create_booking_success(self, client):
        with patch("app.services.booking_service.get_supabase") as mock_sb:
            mock_resp = MagicMock()
            mock_resp.data = [_mock_booking()]
            mock_sb.return_value.table.return_value.insert.return_value.execute.return_value = mock_resp

            resp = client.post("/api/booking/", json={
                "anonymous_id": "anon_abc123",
                "counselor_id": "counselor-uuid-1",
                "scheduled_at": "2026-04-01T10:00:00",
            })
            assert resp.status_code == 201
            data = resp.get_json()
            assert data["message"] == "Booking created"
            assert data["booking"]["status"] == "pending"

    def test_create_booking_missing_fields(self, client):
        resp = client.post("/api/booking/", json={"anonymous_id": "anon_abc123"})
        assert resp.status_code == 400
        assert "Missing fields" in resp.get_json()["error"]

    def test_create_booking_no_body(self, client):
        resp = client.post("/api/booking/")
        assert resp.status_code == 400


class TestGetMyBookings:
    def test_get_my_bookings(self, client):
        with patch("app.services.booking_service.get_supabase") as mock_sb:
            mock_resp = MagicMock()
            mock_resp.data = [_mock_booking()]
            (mock_sb.return_value.table.return_value
             .select.return_value.eq.return_value
             .order.return_value.execute.return_value) = mock_resp

            resp = client.get("/api/booking/my?anonymous_id=anon_abc123")
            assert resp.status_code == 200
            assert len(resp.get_json()["bookings"]) == 1

    def test_get_my_bookings_missing_param(self, client):
        resp = client.get("/api/booking/my")
        assert resp.status_code == 400

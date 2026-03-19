import pytest
from unittest.mock import patch, MagicMock
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _mock_post(overrides=None):
    base = {
        "id": "post-uuid-1",
        "anonymous_id": "anon_xyz",
        "title": "I feel overwhelmed",
        "content": "Exams are too much...",
        "tags": ["stress"],
        "created_at": "2026-03-18T10:00:00",
    }
    if overrides:
        base.update(overrides)
    return base


class TestForumPosts:
    def test_list_posts(self, client):
        with patch("app.services.forum_service.get_supabase") as mock_sb:
            mock_resp = MagicMock()
            mock_resp.data = [_mock_post()]
            (mock_sb.return_value.table.return_value
             .select.return_value.order.return_value
             .range.return_value.execute.return_value) = mock_resp

            resp = client.get("/api/forum/posts")
            assert resp.status_code == 200
            assert len(resp.get_json()["posts"]) == 1

    def test_create_post_success(self, client):
        with patch("app.services.forum_service.get_supabase") as mock_sb:
            mock_resp = MagicMock()
            mock_resp.data = [_mock_post()]
            mock_sb.return_value.table.return_value.insert.return_value.execute.return_value = mock_resp

            resp = client.post("/api/forum/posts", json={
                "anonymous_id": "anon_xyz",
                "title": "I feel overwhelmed",
                "content": "Exams are too much...",
            })
            assert resp.status_code == 201
            assert resp.get_json()["message"] == "Post created"

    def test_create_post_missing_fields(self, client):
        resp = client.post("/api/forum/posts", json={"anonymous_id": "anon_xyz"})
        assert resp.status_code == 400


class TestForumComments:
    def test_add_comment(self, client):
        with patch("app.services.forum_service.get_supabase") as mock_sb:
            mock_resp = MagicMock()
            mock_resp.data = [
                {"id": "comment-1", "post_id": "post-uuid-1",
                 "anonymous_id": "anon_xyz", "content": "You got this!"}
            ]
            mock_sb.return_value.table.return_value.insert.return_value.execute.return_value = mock_resp

            resp = client.post("/api/forum/posts/post-uuid-1/comments", json={
                "anonymous_id": "anon_xyz",
                "content": "You got this!",
            })
            assert resp.status_code == 201

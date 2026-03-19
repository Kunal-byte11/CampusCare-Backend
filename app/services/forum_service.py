from app.services.supabase_client import get_supabase

POSTS_TABLE = "forum_posts"
COMMENTS_TABLE = "forum_comments"


# ── Posts ─────────────────────────────────────────────────────────────────────

def create_post(anonymous_id: str, title: str, content: str, tags: list = None):
    supabase = get_supabase()
    try:
        response = (
            supabase.table(POSTS_TABLE)
            .insert(
                {
                    "anonymous_id": anonymous_id,
                    "title": title,
                    "content": content,
                    "tags": tags or [],
                    "upvotes": 0,
                }
            )
            .execute()
        )
        return response.data[0] if response.data else None, None
    except Exception as e:
        return None, str(e)


def get_posts(limit: int = 20, offset: int = 0):
    supabase = get_supabase()
    try:
        response = (
            supabase.table(POSTS_TABLE)
            .select("*")
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return response.data, None
    except Exception as e:
        return None, str(e)


def get_post_by_id(post_id: str):
    supabase = get_supabase()
    try:
        response = (
            supabase.table(POSTS_TABLE)
            .select("*")
            .eq("id", post_id)
            .single()
            .execute()
        )
        return response.data, None
    except Exception as e:
        return None, str(e)


def delete_post(post_id: str, anonymous_id: str):
    """Only the creator (matched by anonymous_id) can delete their post."""
    supabase = get_supabase()
    try:
        response = (
            supabase.table(POSTS_TABLE)
            .delete()
            .eq("id", post_id)
            .eq("anonymous_id", anonymous_id)
            .execute()
        )
        deleted = len(response.data) > 0 if response.data else False
        return deleted, None
    except Exception as e:
        return False, str(e)


def upvote_post(post_id: str):
    """Atomically increment upvotes by 1 using a Supabase RPC call."""
    supabase = get_supabase()
    try:
        # Fetch current upvotes then increment (atomic update)
        fetch = (
            supabase.table(POSTS_TABLE)
            .select("upvotes")
            .eq("id", post_id)
            .single()
            .execute()
        )
        if not fetch.data:
            return None, "Post not found"
        current = fetch.data.get("upvotes", 0)
        response = (
            supabase.table(POSTS_TABLE)
            .update({"upvotes": current + 1})
            .eq("id", post_id)
            .execute()
        )
        return response.data[0] if response.data else None, None
    except Exception as e:
        return None, str(e)


# ── Comments ──────────────────────────────────────────────────────────────────

def create_comment(post_id: str, anonymous_id: str, content: str):
    supabase = get_supabase()
    try:
        response = (
            supabase.table(COMMENTS_TABLE)
            .insert(
                {
                    "post_id": post_id,
                    "anonymous_id": anonymous_id,
                    "content": content,
                }
            )
            .execute()
        )
        return response.data[0] if response.data else None, None
    except Exception as e:
        return None, str(e)


def get_comments(post_id: str):
    supabase = get_supabase()
    try:
        response = (
            supabase.table(COMMENTS_TABLE)
            .select("*")
            .eq("post_id", post_id)
            .order("created_at")
            .execute()
        )
        return response.data, None
    except Exception as e:
        return None, str(e)


def delete_comment(comment_id: str, anonymous_id: str):
    supabase = get_supabase()
    try:
        response = (
            supabase.table(COMMENTS_TABLE)
            .delete()
            .eq("id", comment_id)
            .eq("anonymous_id", anonymous_id)
            .execute()
        )
        deleted = len(response.data) > 0 if response.data else False
        return deleted, None
    except Exception as e:
        return False, str(e)

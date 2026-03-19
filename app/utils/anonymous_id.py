import uuid


def generate_anonymous_id() -> str:
    """
    Generate a UUID-based anonymous identifier for users who haven't signed up.
    This should be stored client-side (e.g. localStorage) and sent with each request.

    Example usage:
        from app.utils.anonymous_id import generate_anonymous_id
        anon_id = generate_anonymous_id()
        # => "anon_3f2504e0-4f89-11d3-9a0c-0305e82c3301"
    """
    return f"anon_{uuid.uuid4()}"


def is_valid_anonymous_id(anon_id: str) -> bool:
    """Check that a string looks like a valid anonymous ID."""
    if not anon_id or not anon_id.startswith("anon_"):
        return False
    try:
        uuid.UUID(anon_id[5:])
        return True
    except ValueError:
        return False

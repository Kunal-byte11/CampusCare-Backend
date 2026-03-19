"""
auth_guard.py
-------------
Flask decorators to validate Supabase JWTs on protected routes.

Supabase JWTs are standard HS256 tokens signed with SUPABASE_JWT_SECRET.
The payload includes: sub (user UUID), role, email, exp, etc.

Usage:
    from app.utils.auth_guard import auth_required, counselor_required

    @bp.route("/protected")
    @auth_required
    def protected_route():
        user = g.current_user   # dict with JWT payload
        ...
"""

import os
from functools import wraps
from flask import request, jsonify, g
import jwt


def _extract_token() -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


def auth_required(f):
    """Validate the Supabase JWT. Sets g.current_user on success."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_token()
        if not token:
            return jsonify({"error": "Authorization header missing or malformed"}), 401

        secret = os.getenv("SUPABASE_JWT_SECRET")
        if not secret:
            return jsonify({"error": "Server misconfiguration: JWT secret not set"}), 500

        try:
            payload = jwt.decode(
                token,
                secret,
                algorithms=["HS256"],
                audience="authenticated",
            )
            g.current_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"error": f"Invalid token: {e}"}), 401

        return f(*args, **kwargs)
    return decorated


def counselor_required(f):
    """
    Must be applied AFTER @auth_required.
    Checks that the user's app_metadata.role is 'counselor' or 'admin'.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        user = getattr(g, "current_user", None)
        if not user:
            return jsonify({"error": "Unauthenticated"}), 401

        # Supabase stores custom roles in app_metadata
        app_metadata = user.get("app_metadata", {})
        role = app_metadata.get("role", "")
        if role not in ("counselor", "admin"):
            return jsonify({"error": "Forbidden: counselor role required"}), 403

        return f(*args, **kwargs)
    return decorated

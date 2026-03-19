from flask import Blueprint, request, jsonify
from app.services.forum_service import (
    create_post,
    get_posts,
    get_post_by_id,
    delete_post,
    upvote_post,
    create_comment,
    get_comments,
    delete_comment,
)

forum_bp = Blueprint("forum", __name__)


# ── Posts ────────────────────────────────────────────────────────────────────

@forum_bp.route("/posts/", methods=["GET"])
def list_posts():
    """Return paginated forum posts. Query params: ?limit=20&offset=0"""
    limit = int(request.args.get("limit", 20))
    offset = int(request.args.get("offset", 0))
    posts, error = get_posts(limit=limit, offset=offset)
    if error:
        return jsonify({"error": error}), 500
    return jsonify({"posts": posts}), 200


@forum_bp.route("/posts/<post_id>", methods=["GET"])
def get_post(post_id):
    post, error = get_post_by_id(post_id)
    if error:
        return jsonify({"error": error}), 500
    if not post:
        return jsonify({"error": "Post not found"}), 404
    return jsonify({"post": post}), 200


@forum_bp.route("/posts/", methods=["POST"])
def new_post():
    """
    Create a forum post.
    Body: { anonymous_id, title, content }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No JSON body"}), 400

    required = ["anonymous_id", "title", "content"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    post, error = create_post(
        anonymous_id=data["anonymous_id"],
        title=data["title"],
        content=data["content"],
        tags=data.get("tags", []),
    )
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"message": "Post created", "post": post}), 201


@forum_bp.route("/posts/<post_id>", methods=["DELETE"])
def remove_post(post_id):
    """
    Delete a post. Requires the anonymous_id that created it.
    Body: { anonymous_id }
    """
    data = request.get_json(silent=True) or {}
    anonymous_id = data.get("anonymous_id")
    if not anonymous_id:
        return jsonify({"error": "anonymous_id required"}), 400

    success, error = delete_post(post_id, anonymous_id)
    if error:
        return jsonify({"error": error}), 500
    if not success:
        return jsonify({"error": "Not found or unauthorised"}), 403

    return jsonify({"message": "Post deleted"}), 200


@forum_bp.route("/posts/<post_id>/upvote/", methods=["POST"])
def upvote(post_id):
    """Increment upvotes for a post by 1. No auth required."""
    result, error = upvote_post(post_id)
    if error:
        return jsonify({"error": error}), 500
    return jsonify({"message": "Upvoted", "post": result}), 200


# ── Comments ──────────────────────────────────────────────────────────────────

@forum_bp.route("/posts/<post_id>/comments/", methods=["GET"])
def list_comments(post_id):
    comments, error = get_comments(post_id)
    if error:
        return jsonify({"error": error}), 500
    return jsonify({"comments": comments}), 200


@forum_bp.route("/posts/<post_id>/comments/", methods=["POST"])
def add_comment(post_id):
    """Body: { anonymous_id, content }"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No JSON body"}), 400

    required = ["anonymous_id", "content"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    comment, error = create_comment(
        post_id=post_id,
        anonymous_id=data["anonymous_id"],
        content=data["content"],
    )
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"message": "Comment added", "comment": comment}), 201


@forum_bp.route("/comments/<comment_id>", methods=["DELETE"])
def remove_comment(comment_id):
    """Body: { anonymous_id }"""
    data = request.get_json(silent=True) or {}
    anonymous_id = data.get("anonymous_id")
    if not anonymous_id:
        return jsonify({"error": "anonymous_id required"}), 400

    success, error = delete_comment(comment_id, anonymous_id)
    if error:
        return jsonify({"error": error}), 500
    if not success:
        return jsonify({"error": "Not found or unauthorised"}), 403

    return jsonify({"message": "Comment deleted"}), 200

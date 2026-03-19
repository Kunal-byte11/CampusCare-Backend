from flask import Blueprint, request, jsonify
from app.services.ai_service import chat_with_ai, get_chat_history

ai_chat_bp = Blueprint("ai_chat", __name__)


@ai_chat_bp.route("/chat/", methods=["POST"])
def chat():
    """
    Send a message to the AI counselling assistant.
    Body:
      - user_id: str  (Supabase user UUID or anonymous_id)
      - message: str
      - session_id: str (optional — pass existing session to continue)
    Returns:
      - reply: str
      - mood_score: float  (-1.0 negative → 1.0 positive)
      - mood_label: str
      - session_id: str
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No JSON body"}), 400

    required = ["user_id", "message"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    result, error = chat_with_ai(
        user_id=data["user_id"],
        message=data["message"],
        session_id=data.get("session_id"),
    )
    if error:
        return jsonify({"error": error}), 500

    return jsonify(result), 200


@ai_chat_bp.route("/history/", methods=["GET"])
def history():
    """
    Return chat history for a session.
    Query params: ?session_id=<uuid>
    """
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id query param required"}), 400

    messages, error = get_chat_history(session_id)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"messages": messages}), 200

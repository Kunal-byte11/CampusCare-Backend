from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from app.services.agora_service import generate_rtc_token
from app.services.supabase_client import get_supabase
from app.utils.auth_guard import auth_required

video_call_bp = Blueprint("video_call", __name__)


@video_call_bp.route("/token", methods=["GET"])
@auth_required
def get_token():
    """
    Generate an Agora RTC token for a channel.
    Query params:
      - channel: str  (channel name)
      - uid: int      (user UID, 0 for auto-assign)
      - role: str     (publisher | subscriber, default publisher)
    Headers:
      - Authorization: Bearer <supabase_jwt>
    """
    channel = request.args.get("channel")
    if not channel:
        return jsonify({"error": "channel query param required"}), 400

    try:
        uid = int(request.args.get("uid", 0))
    except ValueError:
        return jsonify({"error": "uid must be an integer"}), 400

    role = request.args.get("role", "publisher")
    if role not in ("publisher", "subscriber"):
        return jsonify({"error": "role must be publisher or subscriber"}), 400

    data, error = generate_rtc_token(channel=channel, uid=uid, role=role)
    if error:
        return jsonify({"error": error}), 500

    return jsonify(data), 200


@video_call_bp.route("/start", methods=["POST"])
@auth_required
def start_call():
    """
    Log that a video call has started for a specific booking.
    Body: { "booking_id": "uuid..." }
    """
    data = request.get_json(silent=True)
    if not data or "booking_id" not in data:
        return jsonify({"error": "booking_id required"}), 400

    booking_id = data["booking_id"]
    supabase = get_supabase()

    try:
        supabase.table("bookings").update({
            "call_started_at": datetime.now(timezone.utc).isoformat()
        }).eq("id", booking_id).execute()
    except Exception as e:
        return jsonify({"error": f"Failed to log start time: {e}"}), 500

    return jsonify({"message": "call started", "limit_seconds": 300}), 200

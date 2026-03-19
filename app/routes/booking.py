from flask import Blueprint, request, jsonify
from app.services.booking_service import (
    create_booking,
    get_bookings_for_anonymous,
    get_all_bookings,
    update_booking_status,
)
from app.utils.auth_guard import auth_required, counselor_required

booking_bp = Blueprint("booking", __name__)


@booking_bp.route("/", methods=["POST"])
def book_session():
    """
    Create a new booking.
    Expects JSON body:
      - counselor_id: str
      - scheduled_at: ISO 8601 datetime str
      - anonymous_id: str (generated client-side or by anonymous_id util)
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    required = ["counselor_id", "scheduled_at", "anonymous_id"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    result, error = create_booking(
        anonymous_id=data["anonymous_id"],
        counselor_id=data["counselor_id"],
        scheduled_at=data["scheduled_at"],
        notes=data.get("notes", ""),
    )
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"message": "Booking created", "booking": result}), 201


@booking_bp.route("/my", methods=["GET"])
def get_my_bookings():
    """
    Get all bookings for a given anonymous_id.
    Query param: ?anonymous_id=<uuid>
    """
    anonymous_id = request.args.get("anonymous_id")
    if not anonymous_id:
        return jsonify({"error": "anonymous_id query param required"}), 400

    result, error = get_bookings_for_anonymous(anonymous_id)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"bookings": result}), 200


@booking_bp.route("/all", methods=["GET"])
@auth_required
@counselor_required
def list_all_bookings():
    """
    Counselor/admin endpoint — returns all bookings.
    Requires a valid Supabase JWT with counselor role.
    """
    result, error = get_all_bookings()
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"bookings": result}), 200


@booking_bp.route("/<booking_id>/status", methods=["PATCH"])
@auth_required
@counselor_required
def change_status(booking_id):
    """
    Update booking status (e.g. confirmed, cancelled).
    Expects JSON body: { "status": "confirmed" | "cancelled" | "completed" }
    """
    data = request.get_json(silent=True)
    if not data or "status" not in data:
        return jsonify({"error": "status field required"}), 400

    allowed = {"confirmed", "cancelled", "completed", "pending"}
    if data["status"] not in allowed:
        return jsonify({"error": f"status must be one of {allowed}"}), 400

    result, error = update_booking_status(booking_id, data["status"])
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"message": "Status updated", "booking": result}), 200

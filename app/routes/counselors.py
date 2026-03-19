from flask import Blueprint, request, jsonify
from app.services.counselor_service import (
    get_all_counselors,
    get_counselor_by_id,
    create_counselor,
    update_counselor_availability,
)
from app.utils.auth_guard import auth_required, counselor_required

counselors_bp = Blueprint("counselors", __name__)


@counselors_bp.route("/", methods=["GET"])
def list_counselors():
    """
    List counselors.
    Query param: ?available=true  — filter to available only
    """
    available_only = request.args.get("available", "").lower() == "true"
    result, error = get_all_counselors(available_only=available_only)
    if error:
        return jsonify({"error": error}), 500
    return jsonify({"counselors": result}), 200


@counselors_bp.route("/<counselor_id>", methods=["GET"])
def get_counselor(counselor_id):
    result, error = get_counselor_by_id(counselor_id)
    if error:
        return jsonify({"error": error}), 500
    if not result:
        return jsonify({"error": "Counselor not found"}), 404
    return jsonify({"counselor": result}), 200


@counselors_bp.route("/", methods=["POST"])
@auth_required
@counselor_required
def add_counselor():
    """Admin-only: create a counselor profile. Body: { name, specialization }"""
    data = request.get_json(silent=True)
    if not data or "name" not in data:
        return jsonify({"error": "name is required"}), 400

    result, error = create_counselor(
        name=data["name"],
        specialization=data.get("specialization", ""),
        available=data.get("available", True),
    )
    if error:
        return jsonify({"error": error}), 500
    return jsonify({"message": "Counselor created", "counselor": result}), 201


@counselors_bp.route("/<counselor_id>/availability", methods=["PATCH"])
@auth_required
@counselor_required
def toggle_availability(counselor_id):
    """Body: { available: true | false }"""
    data = request.get_json(silent=True)
    if data is None or "available" not in data:
        return jsonify({"error": "available (bool) is required"}), 400

    result, error = update_counselor_availability(counselor_id, bool(data["available"]))
    if error:
        return jsonify({"error": error}), 500
    return jsonify({"message": "Availability updated", "counselor": result}), 200

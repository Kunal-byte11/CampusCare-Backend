from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.services.supabase_client import get_supabase
from app.utils.anonymous_id import generate_anonymous_id

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register/", methods=["POST"])
def register():
    """
    Register a new student by providing an institutional email and password.
    Returns an anonymous ID and fully discards the email to ensure privacy.
    JSON Body:
      - email: str
      - password: str
    """
    data = request.get_json(silent=True)
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Missing email or password"}), 400

    email = data["email"].strip().lower()
    password = data["password"]

    if not email.endswith("@ltce.in"):
        return jsonify({"error": "Only @ltce.in institutional emails are supported."}), 403

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    supabase = get_supabase()
    anon_id = generate_anonymous_id()
    password_hash = generate_password_hash(password)

    try:
        supabase.table("anonymous_users").insert({
            "anonymous_id": anon_id,
            "password_hash": password_hash
        }).execute()
        return jsonify({"anonymous_id": anon_id}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to create account: {e}"}), 500


@auth_bp.route("/login/", methods=["POST"])
def login():
    """
    Login using an anonymous ID and password.
    JSON Body:
      - anonymous_id: str
      - password: str
    """
    data = request.get_json(silent=True)
    if not data or "anonymous_id" not in data or "password" not in data:
        return jsonify({"error": "Missing anonymous_id or password"}), 400

    anon_id = data["anonymous_id"].strip()
    password = data["password"]

    supabase = get_supabase()
    try:
        response = supabase.table("anonymous_users").select("password_hash").eq("anonymous_id", anon_id).execute()
        
        if not response.data:
            return jsonify({"error": "Invalid anonymous ID or password"}), 401
            
        stored_hash = response.data[0]["password_hash"]
        
        if check_password_hash(stored_hash, password):
            return jsonify({
                "message": "Login successful", 
                "anonymous_id": anon_id,
                "role": "student"
            }), 200
        else:
            return jsonify({"error": "Invalid anonymous ID or password"}), 401
            
    except Exception as e:
        return jsonify({"error": f"Login failed: {e}"}), 500


@auth_bp.route("/counselor/login/", methods=["POST"])
def counselor_login():
    """
    Login for counselors.
    JSON Body: { email, password }
    """
    data = request.get_json(silent=True)
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Missing email or password"}), 400

    email = data["email"].strip().lower()
    password = data["password"]

    supabase = get_supabase()
    try:
        # We expect 'email' and 'password_hash' columns to be added by the user
        response = supabase.table("counselors").select("id, name, password_hash").eq("email", email).execute()
        
        if not response.data:
            return jsonify({"error": "Invalid email or password"}), 401
            
        counselor = response.data[0]
        if check_password_hash(counselor["password_hash"], password):
            return jsonify({
                "message": "Login successful",
                "counselor_id": counselor["id"],
                "name": counselor["name"],
                "role": "counselor"
            }), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401
            
    except Exception as e:
        # If columns don't exist yet, return a clear error
        if "column" in str(e).lower():
            return jsonify({"error": "Database schema update required. Please run the SQL in implementation_plan.md"}), 500
        return jsonify({"error": f"Counselor login failed: {e}"}), 500


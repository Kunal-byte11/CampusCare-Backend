from app.services.supabase_client import get_supabase


TABLE = "bookings"


def create_booking(anonymous_id: str, counselor_id: str, scheduled_at: str, notes: str = ""):
    """Insert a new booking row and return (data, error)."""
    supabase = get_supabase()
    try:
        response = (
            supabase.table(TABLE)
            .insert(
                {
                    "anonymous_id": anonymous_id,
                    "counselor_id": counselor_id,
                    "scheduled_at": scheduled_at,
                    "notes": notes,
                    "status": "pending",
                }
            )
            .execute()
        )
        return response.data[0] if response.data else None, None
    except Exception as e:
        return None, str(e)


def get_bookings_for_anonymous(anonymous_id: str):
    """Fetch all bookings for a given anonymous_id."""
    supabase = get_supabase()
    try:
        response = (
            supabase.table(TABLE)
            .select("*")
            .eq("anonymous_id", anonymous_id)
            .order("scheduled_at", desc=True)
            .execute()
        )
        return response.data, None
    except Exception as e:
        return None, str(e)


def get_all_bookings():
    """Fetch all bookings (counselor/admin use)."""
    supabase = get_supabase()
    try:
        response = (
            supabase.table(TABLE)
            .select("*")
            .order("scheduled_at", desc=True)
            .execute()
        )
        return response.data, None
    except Exception as e:
        return None, str(e)


def update_booking_status(booking_id: str, status: str):
    """Update the status of a booking."""
    supabase = get_supabase()
    try:
        response = (
            supabase.table(TABLE)
            .update({"status": status})
            .eq("id", booking_id)
            .execute()
        )
        return response.data[0] if response.data else None, None
    except Exception as e:
        return None, str(e)

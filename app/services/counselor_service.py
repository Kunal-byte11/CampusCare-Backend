from app.services.supabase_client import get_supabase

TABLE = "counselors"


def get_all_counselors(available_only: bool = False):
    """Fetch all counselors, optionally filtering by availability."""
    supabase = get_supabase()
    try:
        query = supabase.table(TABLE).select("*").order("name")
        if available_only:
            query = query.eq("available", True)
        response = query.execute()
        return response.data, None
    except Exception as e:
        return None, str(e)


def get_counselor_by_id(counselor_id: str):
    supabase = get_supabase()
    try:
        response = (
            supabase.table(TABLE)
            .select("*")
            .eq("id", counselor_id)
            .single()
            .execute()
        )
        return response.data, None
    except Exception as e:
        return None, str(e)


def create_counselor(name: str, specialization: str = "", available: bool = True):
    supabase = get_supabase()
    try:
        response = (
            supabase.table(TABLE)
            .insert({"name": name, "specialization": specialization, "available": available})
            .execute()
        )
        return response.data[0] if response.data else None, None
    except Exception as e:
        return None, str(e)


def update_counselor_availability(counselor_id: str, available: bool):
    supabase = get_supabase()
    try:
        response = (
            supabase.table(TABLE)
            .update({"available": available})
            .eq("id", counselor_id)
            .execute()
        )
        return response.data[0] if response.data else None, None
    except Exception as e:
        return None, str(e)

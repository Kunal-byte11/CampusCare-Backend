from app.services.supabase_client import get_supabase
from werkzeug.security import generate_password_hash

def cleanup():
    supabase = get_supabase()
    
    booking_counselor_id = "7b4cf658-3eeb-4bbe-af91-3580f4cfaead"
    wrong_id = "e744e943-b419-490a-b802-38406fcdf197"
    
    # 1. Delete the wrong one
    res = supabase.table("counselors").delete().eq("id", wrong_id).execute()
    print("Deleted wrong counselor ID.")
    
    # 2. Ensure the correct one has the right credentials
    data = {
        "email": "neetu.hooda@ltce.in",
        "password_hash": generate_password_hash("password123")
    }
    supabase.table("counselors").update(data).eq("id", booking_counselor_id).execute()
    print("Updated correct counselor record.")

if __name__ == "__main__":
    cleanup()

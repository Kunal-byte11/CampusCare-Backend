from app.services.supabase_client import get_supabase

def check_db():
    supabase = get_supabase()
    
    print("--- Counselors ---")
    c = supabase.table("counselors").select("id, name, email").execute()
    for row in c.data:
        print(row)
        
    print("\n--- Bookings ---")
    b = supabase.table("bookings").select("id, counselor_id, anonymous_id, scheduled_at, status").execute()
    for row in b.data:
        print(row)

if __name__ == "__main__":
    check_db()

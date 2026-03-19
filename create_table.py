import os
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

sql = """
CREATE TABLE IF NOT EXISTS anonymous_users (
  anonymous_id TEXT PRIMARY KEY,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
"""
# Supabase Python client doesn't support raw SQL easily unless using rpc, 
# so we'll just print instructions to the user or execute via REST if possible.
# Actually, the user can just add it themselves, OR we can try to do it via the REST API if we have the service key, 
# but the easiest way is to ask the user to run the SQL in their Supabase console.

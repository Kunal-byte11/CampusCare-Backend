"""
extensions.py
-------------
Centralised place to initialise Flask extensions that need to be shared
across modules without causing circular imports.

CORS is initialised directly in the app factory (app/__init__.py).
The Supabase client lives in app/services/supabase_client.py.
"""

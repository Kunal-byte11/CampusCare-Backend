import os
import uuid
import google.generativeai as genai
from app.services.supabase_client import get_supabase
from app.utils.sentiment import analyze_sentiment

TABLE = "chat_sessions"

def _configure_gemini():
    """Configure the Gemini SDK with the API key (idempotent)."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY must be set in your .env file.")
    genai.configure(api_key=api_key)

SYSTEM_PROMPT = (
    "You are CampusCare AI, a compassionate and non-judgmental mental health "
    "support assistant for university students. Your role is to:\n"
    "- Listen empathetically and reflect feelings back to the user\n"
    "- Provide coping strategies and mental health resources\n"
    "- Encourage professional help when appropriate\n"
    "- Keep responses concise (2-4 sentences unless more detail is explicitly needed)\n"
    "- Never diagnose, prescribe, or replace a licensed counsellor\n"
    "- If the user expresses imminent danger to themselves or others, immediately recommend "
    "contacting emergency services or a crisis hotline."
)


CRISIS_TERMS = {
    "suicide", "suicidal", "kill myself", "end my life", "want to die",
    "self harm", "self-harm", "hurt myself", "no reason to live",
}


def _is_flagged(text: str) -> bool:
    """Detect crisis/emergency keywords in the user's message."""
    lowered = text.lower()
    return any(term in lowered for term in CRISIS_TERMS)


def _load_session(session_id: str) -> list[dict]:
    """Load existing messages from Supabase for a session."""
    supabase = get_supabase()
    try:
        response = (
            supabase.table(TABLE)
            .select("messages")
            .eq("id", session_id)
            .single()
            .execute()
        )
        return response.data.get("messages", []) if response.data else []
    except Exception:
        return []


def _save_session(session_id: str, user_id: str, messages: list[dict], mood_score: float, flagged: bool = False):
    """Upsert the session row in Supabase."""
    supabase = get_supabase()
    supabase.table(TABLE).upsert(
        {
            "id": session_id,
            "user_id": user_id,
            "messages": messages,
            "mood_score": mood_score,
            "flagged": flagged,
        }
    ).execute()


def chat_with_ai(user_id: str, message: str, session_id: str | None = None):
    """
    Send a message to the AI assistant, persist history in Supabase.
    Returns (result_dict, error_str).
    """
    session_id = session_id or str(uuid.uuid4())

    # Load conversation history
    history = _load_session(session_id)

    # Append user message
    history.append({"role": "user", "parts": [message]})

    # Build Gemini chat history (exclude the last user message — passed via send_message)
    gemini_history = history[:-1]

    try:
        _configure_gemini()
        model = genai.GenerativeModel(
            model_name=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            system_instruction=SYSTEM_PROMPT,
        )
        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(message)
        reply = response.text.strip()
    except Exception as e:
        return None, f"Gemini API error: {e}"

    # Append assistant reply in Gemini format
    history.append({"role": "model", "parts": [reply]})

    # Sentiment analysis + crisis detection on user message
    mood_score, mood_label = analyze_sentiment(message)
    flagged = _is_flagged(message)

    # Persist session
    try:
        _save_session(session_id, user_id, history, mood_score, flagged)
    except Exception:
        pass  # Non-fatal

    return {
        "reply": reply,
        "mood_score": mood_score,
        "mood_label": mood_label,
        "session_id": session_id,
        "flagged": flagged,
    }, None


def get_chat_history(session_id: str):
    """Return list of messages for a session."""
    supabase = get_supabase()
    try:
        response = (
            supabase.table(TABLE)
            .select("messages, mood_score, created_at")
            .eq("id", session_id)
            .single()
            .execute()
        )
        return response.data, None
    except Exception as e:
        return None, str(e)

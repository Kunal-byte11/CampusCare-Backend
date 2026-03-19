import os
import time
from flask import current_app

try:
    from agora_token_builder import RtcTokenBuilder
    AGORA_AVAILABLE = True
except ImportError:
    AGORA_AVAILABLE = False


ROLE_MAP = {
    "publisher": 1,   # Role_Publisher
    "subscriber": 2,  # Role_Subscriber
}

TOKEN_EXPIRY_SECONDS = 300  # 5 minutes


def generate_rtc_token(channel: str, uid: int, role: str = "publisher"):
    """
    Generate an Agora RTC token.
    Returns (token_str, error_str).
    """
    if not AGORA_AVAILABLE:
        return None, (
            "agora-token package is not installed. "
            "Run: pip install agora-token-builder"
        )

    app_id = os.getenv("AGORA_APP_ID")
    app_cert = os.getenv("AGORA_APP_CERT")

    if not app_id or not app_cert:
        return None, "AGORA_APP_ID and AGORA_APP_CERT must be set in .env"

    agora_role = ROLE_MAP.get(role, 1)
    expire_timestamp = int(time.time()) + TOKEN_EXPIRY_SECONDS

    try:
        token = RtcTokenBuilder.buildTokenWithUid(
            app_id,
            app_cert,
            channel,
            uid,
            agora_role,
            expire_timestamp,
        )
        data = {
            "token": token,
            "channel": channel,
            "uid": uid,
            "app_id": app_id,
            "expires_in": TOKEN_EXPIRY_SECONDS,
        }
        return data, None
    except Exception as e:
        return None, f"Agora token generation failed: {e}"

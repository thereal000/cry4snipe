# cry4snipe/utils.py
import random
import string
import json
import os
from typing import Optional
from datetime import datetime
import requests
from constants import (
    HEADERS,
    CHARS,
    DEFAULT_CONFIG,
    REQUEST_TIMEOUT,
    WEBHOOK_TIMEOUT,
)
def random_string(length: int, chars: str = CHARS) -> str:

    return ''.join(random.choice(chars) for _ in range(length))


def generate_register_payload(username: str) -> dict:
   
    return {
        "fingerprint": f"{random.randint(10**16, 10**17)}.{random_string(20)}",
        "email": f"{random_string(10)}@gmail.com",
        "username": username,
        "global_name": random_string(8),
        "password": random_string(12),
        "invite": None,
        "consent": True,
        "date_of_birth": "2000-01-01",
        "gift_code_sku_id": None,
        "promotional_email_opt_in": False,
    }
def is_username_taken(data: dict) -> bool:
   
    if "taken" in data:
        return data["taken"]
    errors = data.get("errors", {}).get("username", {}).get("_errors", [])
    return any(e.get("code") == "USERNAME_ALREADY_TAKEN" for e in errors)

def sanitize_proxy(raw: str) -> Optional[str]:
    
    raw = raw.strip()
    if not raw:
        return None
    if raw.startswith("socks"):
        return None
    if not raw.startswith(("http://", "https://")):
        raw = "http://" + raw
    return raw
def send_webhook(url: str, username: str, taken: bool = False) -> bool:
   
    if not url:
        return True
    color = 15158332 if taken else 3066993
    title = "Username unavailable" if taken else "Username available!"
    desc = f"`{username}` is {'already taken' if taken else 'free to claim!'}"
    try:
        requests.post(
            url,
            json={
                "embeds": [
                    {
                        "title": title,
                        "description": desc,
                        "color": color,
                        "timestamp": datetime.utcnow().isoformat(),
                        "footer": {"text": "cry4snipe by cry4me"},
                    }
                ]
            },
            timeout=WEBHOOK_TIMEOUT,
        )
        return True
    except Exception:
        return False
def load_config() -> dict:
    
    cfg_file = DEFAULT_CONFIG["config_file"]
    if os.path.exists(cfg_file):
        with open(cfg_file, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # Fichier corrompu, on retourne la config par défaut
                return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config: dict) -> None:
    
    with open(DEFAULT_CONFIG["config_file"], "w") as f:
        json.dump(config, f, indent=4)

# cry4snipe/sniper.py
# Thread de sniping – cœur du programme

import threading
import time
import json
from typing import Optional

import requests
from requests.exceptions import (
    ProxyError,
    SSLError,
    ConnectTimeout,
    ReadTimeout,
    ConnectionError as ReqConnErr,
)

from constants import (
    API_USERNAME_CHECK,
    API_REGISTER,
    HEADERS,
    CHARS,
    REQUEST_TIMEOUT,
)
from utils import (
    generate_register_payload,
    is_username_taken,
    send_webhook,
    random_string,
)
class SniperThread(threading.Thread):
    
    def __init__(self, callbacks, config: dict):
        super().__init__(daemon=True)
        self.callbacks = callbacks
        self.config = config

        # État du thread
        self.running = False
        self.checked = 0
        self.available = 0

        # Alternance entre les deux APIs (0 = check, 1 = register)
        self.cycle = 0

        # Backoff exponentiel pour les rate limits
        self.backoff_seconds = 1
        self.max_backoff = 60

    def run(self):
       
        self.running = True
        delay = float(self.config.get("delay", 5.0))
        length = int(self.config.get("length", 5))
        verify_ssl = not self.config.get("no_verify", False)
        zero_delay = self.config.get("zero_delay", False)
        webhook_url = self.config.get("webhook", "")

        # Vérification de la disponibilité des proxies
        proxy_available = bool(self.callbacks.proxy_list)

        # Sécurité : délai minimum
        if zero_delay and proxy_available:
            delay = 0.0
        else:
            min_delay = 2 if proxy_available else 5
            if delay < min_delay:
                self.callbacks.log(f"⚠️ Délai trop bas → forcé à {min_delay}s", "yellow")
                delay = min_delay

        # Boucle principale
        while self.running:
            try:
                time.sleep(delay)
            except:
                break

            # Génération du nom
            username = random_string(length, chars=CHARS)
            self.checked += 1
            self.callbacks.update_checked(self.checked)

            # Tentatives avec les proxies
            success = False
            attempts = 0
            max_attempts = len(self.callbacks.proxy_list) if proxy_available else 1

            while not success and attempts < max_attempts and self.running:
                attempts += 1
                proxy = self.callbacks.get_next_proxy() if proxy_available else None

                try:
                    # Choix de l'API
                    api_url = API_USERNAME_CHECK if self.cycle == 0 else API_REGISTER
                    payload = (
                        {"username": username}
                        if self.cycle == 0
                        else generate_register_payload(username)
                    )

                    # Requête HTTP
                    resp = requests.post(
                        api_url,
                        json=payload,
                        headers=HEADERS,
                        proxies={"http": proxy, "https": proxy} if proxy else None,
                        timeout=REQUEST_TIMEOUT,
                        verify=verify_ssl,
                    )

                    # --- Gestion des codes HTTP ---

                    # Proxy mort (blacklisté par Discord)
                    if resp.status_code in (400, 403, 502, 503, 504):
                        self.callbacks.log(
                            f"[{self.checked}] {username} — Proxy mort (HTTP {resp.status_code})",
                            "yellow",
                        )
                        if proxy:
                            self.callbacks.remove_proxy(proxy)
                        continue

                    # Rate limit – backoff exponentiel
                    if resp.status_code == 429:
                        self.callbacks.log(
                            f"[{self.checked}] {username} — RATE LIMIT, backoff {self.backoff_seconds}s",
                            "yellow",
                        )
                        time.sleep(self.backoff_seconds)
                        self.backoff_seconds = min(
                            self.backoff_seconds * 2, self.max_backoff
                        )
                        self.cycle = 1 - self.cycle  # bascule vers l'autre API
                        continue

                    # Réinitialisation du backoff en cas de succès
                    self.backoff_seconds = 1

                    # Autres erreurs HTTP
                    if resp.status_code != 200:
                        self.callbacks.log(
                            f"[{self.checked}] {username} — HTTP {resp.status_code}",
                            "red",
                        )
                        continue

                    # --- Traitement de la réponse ---

                    try:
                        data = resp.json()
                    except json.JSONDecodeError:
                        self.callbacks.log(
                            f"[{self.checked}] {username} — Réponse non-JSON",
                            "red",
                        )
                        continue

                    taken = is_username_taken(data)
                    success = True

                    if taken:
                        self.callbacks.log(f"[{self.checked}] {username} PRIS", "red")
                        self.callbacks.add_taken(username)
                        if webhook_url:
                            ok = send_webhook(webhook_url, username, taken=True)
                            if not ok:
                                self.callbacks.log(
                                    f"[{self.checked}] Webhook échoué pour {username}",
                                    "yellow",
                                )
                    else:
                        self.available += 1
                        self.callbacks.log(
                            f"[{self.checked}] {username} DISPONIBLE !!!",
                            "green",
                        )
                        self.callbacks.save_valid(username)
                        if webhook_url:
                            ok = send_webhook(webhook_url, username, taken=False)
                            if not ok:
                                self.callbacks.log(
                                    f"[{self.checked}] Webhook échoué pour {username}",
                                    "yellow",
                                )

                # --- Gestion des exceptions réseau ---
                except (SSLError, ProxyError, ConnectTimeout, ReadTimeout, ReqConnErr) as e:
                    self.callbacks.log(
                        f"[{self.checked}] {username} — Erreur proxy/connexion : {e}",
                        "red",
                    )
                    if proxy:
                        self.callbacks.remove_proxy(proxy)

                # --- Gestion des autres exceptions (non prévues) ---
                except Exception as e:
                    self.callbacks.log(
                        f"[{self.checked}] {username} — Erreur inattendue : {e}",
                        "red",
                    )
                    # On continue, mais on loggue l'erreur pour debug
                    continue

            if not success:
                self.callbacks.log(
                    f"[{self.checked}] {username} — ÉCHEC après {attempts} tentatives",
                    "yellow",
                )

        # Fin du thread
        self.callbacks.log("Sniping arrêté.")
        self.callbacks.update_status("Arrêté.")

    def stop(self):
        """Arrête proprement le thread."""
        self.running = False

# cry4snipe/constants.py
# Toutes les constantes du projet

# URL des API Discord 
API_USERNAME_CHECK = "https://discord.com/api/v9/unique-username/username-attempt-unauthed"
API_REGISTER = "https://discord.com/api/v9/auth/register"

# --- Headers HTTP ---
HEADERS = {"Content-Type": "application/json"}

CHARS = 'abcdefghijklmnopqrstuvwxyz0123456789_.'

# --- Timeouts réseau (en secondes) ---
REQUEST_TIMEOUT = 8          # pour les appels api
WEBHOOK_TIMEOUT = 10         # pour les webhooks

# --- Configuration par défaut ---
DEFAULT_CONFIG = {
    "delay": 5.0,            # délai entre chaque tentative (secondes)
    "length": 5,             # longueur du nom à générer
    "webhook": "",           # URL du webhook Discord
    "no_verify": False,      # désactiver la vérification SSL
    "zero_delay": False,     # délai nul si proxies chargés
    "proxy_file": "proxies.txt",
    "valid_file": "valid.txt",
    "config_file": "config.json"
}

# --- Limites pour l'interface ---
MAX_LOG_LINES = 1000         # nombre maximum de lignes dans le log UI
VALID_BUFFER_SIZE = 10       # nombre de noms à bufferiser avant écriture
# cry4snipe/gui.py
# Interface graphique avec tkinter

import os
import threading
from collections import deque
from tkinter import (
    Tk,
    Frame,
    Label,
    Entry,
    Button,
    Text,
    Scrollbar,
    END,
    DISABLED,
    NORMAL,
    StringVar,
    BooleanVar,
    Checkbutton,
    messagebox,
    ttk,
)
from tkinter.ttk import Style, Notebook

from constants import DEFAULT_CONFIG, MAX_LOG_LINES, VALID_BUFFER_SIZE
from utils import load_config, save_config, sanitize_proxy
from sniper import SniperThread


class Cry4SnipeApp:
    """Application principale de sniping avec interface moderne."""

    def __init__(self):
        self.root = Tk()
        self.root.title("❄️ cry4snipe – Username Sniper v4")
        self.root.resizable(False, False)
        self.root.configure(bg="#0d1117")
        self._center_window(720, 580)

        # --- Configuration ---
        self.config = load_config()
        self.delay_var = StringVar(value=str(self.config.get("delay", 5.0)))
        self.length_var = StringVar(value=str(self.config.get("length", 5)))
        self.webhook_var = StringVar(value=self.config.get("webhook", ""))
        self.no_verify_var = BooleanVar(value=self.config.get("no_verify", False))
        self.zero_delay_var = BooleanVar(value=self.config.get("zero_delay", False))

        # --- Proxies (thread-safe) ---
        self.proxy_list = []
        self.proxy_index = -1
        self.proxy_lock = threading.Lock()

        # --- Sniping ---
        self.sniper = None

        # --- Résultats ---
        self.taken_queue = deque(maxlen=50)
        self.valid_buffer = []
        self.BUFFER_SIZE = VALID_BUFFER_SIZE

        # --- Fichiers ---
        self.valid_file = self.config.get("valid_file", "valid.txt")
        self.proxies_file = self.config.get("proxy_file", "proxies.txt")

        # --- UI ---
        self._set_modern_theme()
        self._build_ui()
        self.load_proxies_from_file()
        self.load_valid_usernames()

        # --- Gestion de la fermeture ---
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _center_window(self, w, h):
        """Centre la fenêtre à l'écran."""
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(ws - w) // 2}+{(hs - h) // 2}")

    def _set_modern_theme(self):
        """Applique un thème sombre moderne avec accents."""
        style = Style()
        style.theme_use("clam")

        # --- Couleurs principales ---
        BG_DARK = "#0d1117"
        BG_MEDIUM = "#161b22"
        BG_LIGHT = "#21262d"
        BG_INPUT = "#0d1117"
        FG_PRIMARY = "#f0f6fc"
        FG_SECONDARY = "#8b949e"
        ACCENT_BLUE = "#58a6ff"
        ACCENT_GREEN = "#3fb950"
        ACCENT_RED = "#f85149"
        ACCENT_YELLOW = "#d29922"
        BORDER = "#30363d"

        # --- Style global ---
        style.configure(
            ".",
            background=BG_DARK,
            foreground=FG_PRIMARY,
            fieldbackground=BG_INPUT,
            borderwidth=1,
            focusthickness=0,
        )

        # --- Notebook (onglets) ---
        style.configure(
            "TNotebook",
            background=BG_DARK,
            borderwidth=0,
            tabmargins=[0, 0, 0, 0],
        )
        style.configure(
            "TNotebook.Tab",
            background=BG_MEDIUM,
            foreground=FG_SECONDARY,
            padding=[16, 8],
            font=("Segoe UI", 10),
            borderwidth=0,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", BG_LIGHT)],
            foreground=[("selected", FG_PRIMARY)],
        )

        # --- Frames ---
        style.configure("TFrame", background=BG_DARK)
        style.configure("Card.TFrame", background=BG_MEDIUM, relief="flat")

        # --- Labels ---
        style.configure(
            "TLabel",
            background=BG_DARK,
            foreground=FG_PRIMARY,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Title.TLabel",
            background=BG_DARK,
            foreground=FG_PRIMARY,
            font=("Segoe UI", 12, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=BG_DARK,
            foreground=FG_SECONDARY,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Accent.TLabel",
            background=BG_DARK,
            foreground=ACCENT_BLUE,
            font=("Segoe UI", 10, "bold"),
        )

        # --- Entries ---
        style.configure(
            "TEntry",
            fieldbackground=BG_INPUT,
            foreground=FG_PRIMARY,
            insertcolor=FG_PRIMARY,
            font=("Consolas", 10),
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "TEntry",
            fieldbackground=[("focus", BG_MEDIUM)],
        )

        # --- Boutons ---
        style.configure(
            "Start.TButton",
            background=ACCENT_GREEN,
            foreground=BG_DARK,
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            focusthickness=0,
            padding=[16, 8],
        )
        style.map(
            "Start.TButton",
            background=[("active", "#2ea043"), ("disabled", "#2d4a33")],
            foreground=[("disabled", "#6e7a6e")],
        )

        style.configure(
            "Stop.TButton",
            background=ACCENT_RED,
            foreground=BG_DARK,
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            focusthickness=0,
            padding=[16, 8],
        )
        style.map(
            "Stop.TButton",
            background=[("active", "#da3633"), ("disabled", "#4a2d2d")],
            foreground=[("disabled", "#7a6e6e")],
        )

        style.configure(
            "Action.TButton",
            background=BG_LIGHT,
            foreground=FG_PRIMARY,
            font=("Segoe UI", 9),
            borderwidth=0,
            focusthickness=0,
            padding=[12, 6],
        )
        style.map(
            "Action.TButton",
            background=[("active", BG_MEDIUM)],
        )

        # --- Checkbuttons ---
        style.configure(
            "TCheckbutton",
            background=BG_DARK,
            foreground=FG_SECONDARY,
            font=("Segoe UI", 9),
        )
        style.map(
            "TCheckbutton",
            foreground=[("selected", FG_PRIMARY)],
        )

        # --- Scrollbar ---
        style.configure(
            "Vertical.TScrollbar",
            background=BG_MEDIUM,
            troughcolor=BG_DARK,
            borderwidth=0,
        )

        # --- Text widgets (logs, résultats) ---
        self.root.option_add("*Text.background", BG_INPUT)
        self.root.option_add("*Text.foreground", FG_PRIMARY)
        self.root.option_add("*Text.insertBackground", FG_PRIMARY)
        self.root.option_add("*Text.font", ("Consolas", 9))

    def _build_ui(self):
        """Construit l'interface utilisateur avec style moderne."""
        # --- En-tête ---
        header = Frame(self.root, bg="#0d1117", height=50)
        header.pack(fill="x", pady=(8, 0))
        title = Label(
            header,
            text="❄️ cry4snipe",
            font=("Segoe UI", 18, "bold"),
            bg="#0d1117",
            fg="#f0f6fc",
        )
        title.pack(side="left", padx=(20, 0))
        subtitle = Label(
            header,
            text="Username Sniper v4",
            font=("Segoe UI", 10),
            bg="#0d1117",
            fg="#8b949e",
        )
        subtitle.pack(side="left", padx=(8, 0))

        # --- Séparateur ---
        sep = Frame(self.root, bg="#21262d", height=1)
        sep.pack(fill="x", pady=(8, 12))

        # --- Notebook ---
        notebook = Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self._build_config_tab(notebook)
        self._build_proxy_tab(notebook)
        self._build_log_tab(notebook)
        self._build_results_tab(notebook)

    def _build_config_tab(self, notebook):
        """Onglet de configuration avec style moderne."""
        cfg = Frame(notebook, bg="#0d1117")
        notebook.add(cfg, text="⚙️ Contrôle")

        # --- Card : Paramètres ---
        card1 = Frame(cfg, bg="#161b22", relief="flat")
        card1.pack(fill="x", padx=4, pady=6)

        # Titre de la card
        title = Label(
            card1,
            text="🎯 Paramètres de sniping",
            font=("Segoe UI", 11, "bold"),
            bg="#161b22",
            fg="#f0f6fc",
        )
        title.pack(anchor="w", padx=16, pady=(12, 8))

        # Ligne 1 : Délai + Longueur
        row1 = Frame(card1, bg="#161b22")
        row1.pack(fill="x", padx=16, pady=4)

        Label(row1, text="Délai (s)", bg="#161b22", fg="#8b949e", font=("Segoe UI", 9)).pack(
            side="left", padx=(0, 4)
        )
        Entry(row1, textvariable=self.delay_var, width=8, bg="#0d1117", fg="#f0f6fc").pack(
            side="left", padx=(0, 24)
        )

        Label(row1, text="Longueur", bg="#161b22", fg="#8b949e", font=("Segoe UI", 9)).pack(
            side="left", padx=(0, 4)
        )
        Entry(row1, textvariable=self.length_var, width=8, bg="#0d1117", fg="#f0f6fc").pack(
            side="left"
        )

        # Ligne 2 : Webhook
        row2 = Frame(card1, bg="#161b22")
        row2.pack(fill="x", padx=16, pady=4)

        Label(row2, text="Webhook", bg="#161b22", fg="#8b949e", font=("Segoe UI", 9)).pack(
            side="left", padx=(0, 4)
        )
        Entry(
            row2,
            textvariable=self.webhook_var,
            width=50,
            bg="#0d1117",
            fg="#f0f6fc",
            font=("Consolas", 9),
        ).pack(side="left", fill="x", expand=True)

        # Ligne 3 : Options
        row3 = Frame(card1, bg="#161b22")
        row3.pack(fill="x", padx=16, pady=8)

        Checkbutton(
            row3,
            text="🔓 Désactiver SSL",
            variable=self.no_verify_var,
            bg="#161b22",
            fg="#8b949e",
            selectcolor="#161b22",
            font=("Segoe UI", 9),
        ).pack(side="left", padx=(0, 16))

        Checkbutton(
            row3,
            text="⚡ Délai nul (risqué)",
            variable=self.zero_delay_var,
            bg="#161b22",
            fg="#8b949e",
            selectcolor="#161b22",
            font=("Segoe UI", 9),
        ).pack(side="left")

        # --- Card : Contrôle ---
        card2 = Frame(cfg, bg="#161b22", relief="flat")
        card2.pack(fill="x", padx=4, pady=6)

        title2 = Label(
            card2,
            text="🎮 Contrôle du sniper",
            font=("Segoe UI", 11, "bold"),
            bg="#161b22",
            fg="#f0f6fc",
        )
        title2.pack(anchor="w", padx=16, pady=(12, 8))

        # Boutons
        btn_frame = Frame(card2, bg="#161b22")
        btn_frame.pack(fill="x", padx=16, pady=(0, 12))

        self.start_btn = ttk.Button(
            btn_frame,
            text="▶ DÉMARRER",
            style="Start.TButton",
            command=self.start_sniper,
            width=14,
        )
        self.start_btn.pack(side="left", padx=(0, 12))

        self.stop_btn = ttk.Button(
            btn_frame,
            text="⏹ ARRÊTER",
            style="Stop.TButton",
            command=self.stop_sniper,
            width=14,
            state=DISABLED,
        )
        self.stop_btn.pack(side="left")

        # --- Card : Statistiques ---
        card3 = Frame(cfg, bg="#161b22", relief="flat")
        card3.pack(fill="x", padx=4, pady=6)

        stats_frame = Frame(card3, bg="#161b22")
        stats_frame.pack(fill="x", padx=16, pady=12)

        # Vérifiés
        stat1 = Frame(stats_frame, bg="#161b22")
        stat1.pack(side="left", padx=(0, 24))
        Label(
            stat1,
            text="🔍 Vérifiés",
            bg="#161b22",
            fg="#8b949e",
            font=("Segoe UI", 9),
        ).pack()
        self.checked_lbl = Label(
            stat1,
            text="0",
            bg="#161b22",
            fg="#58a6ff",
            font=("Segoe UI", 16, "bold"),
        )
        self.checked_lbl.pack()

        # Disponibles
        stat2 = Frame(stats_frame, bg="#161b22")
        stat2.pack(side="left", padx=(0, 24))
        Label(
            stat2,
            text="✅ Disponibles",
            bg="#161b22",
            fg="#8b949e",
            font=("Segoe UI", 9),
        ).pack()
        self.avail_lbl = Label(
            stat2,
            text="0",
            bg="#161b22",
            fg="#3fb950",
            font=("Segoe UI", 16, "bold"),
        )
        self.avail_lbl.pack()

        # Statut
        stat3 = Frame(stats_frame, bg="#161b22")
        stat3.pack(side="left")
        Label(
            stat3,
            text="📡 Statut",
            bg="#161b22",
            fg="#8b949e",
            font=("Segoe UI", 9),
        ).pack()
        self.status_lbl = Label(
            stat3,
            text="Prêt",
            bg="#161b22",
            fg="#58a6ff",
            font=("Segoe UI", 12, "bold"),
        )
        self.status_lbl.pack()

    def _build_proxy_tab(self, notebook):
        """Onglet des proxies avec style moderne."""
        pxy = Frame(notebook, bg="#0d1117")
        notebook.add(pxy, text="🌐 Proxies")

        # --- Card ---
        card = Frame(pxy, bg="#161b22", relief="flat")
        card.pack(fill="both", expand=True, padx=4, pady=6)

        title = Label(
            card,
            text="🌐 Gestion des proxies",
            font=("Segoe UI", 11, "bold"),
            bg="#161b22",
            fg="#f0f6fc",
        )
        title.pack(anchor="w", padx=16, pady=(12, 8))

        # Éditeur de proxies
        self.proxy_text = Text(
            card,
            height=10,
            bg="#0d1117",
            fg="#f0f6fc",
            insertbackground="#f0f6fc",
            font=("Consolas", 9),
            relief="flat",
            borderwidth=0,
            wrap="none",
        )
        self.proxy_text.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        # Boutons
        btn_frame = Frame(card, bg="#161b22")
        btn_frame.pack(fill="x", padx=16, pady=(0, 12))

        ttk.Button(
            btn_frame,
            text="📂 Charger",
            style="Action.TButton",
            command=self.load_proxies_from_file,
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            btn_frame,
            text="💾 Sauvegarder",
            style="Action.TButton",
            command=self.save_proxies_to_file,
        ).pack(side="left", padx=(0, 8))

        self.proxy_cnt = Label(
            btn_frame,
            text="0 chargés",
            bg="#161b22",
            fg="#8b949e",
            font=("Segoe UI", 9),
        )
        self.proxy_cnt.pack(side="right")

    def _build_log_tab(self, notebook):
        """Onglet des logs avec style moderne."""
        log = Frame(notebook, bg="#0d1117")
        notebook.add(log, text="📋 Logs")

        # --- Card ---
        card = Frame(log, bg="#161b22", relief="flat")
        card.pack(fill="both", expand=True, padx=4, pady=6)

        # Titre et bouton
        header = Frame(card, bg="#161b22")
        header.pack(fill="x", padx=16, pady=(12, 8))

        Label(
            header,
            text="📋 Console de logs",
            font=("Segoe UI", 11, "bold"),
            bg="#161b22",
            fg="#f0f6fc",
        ).pack(side="left")

        ttk.Button(
            header,
            text="🗑️ Effacer",
            style="Action.TButton",
            command=self.clear_log,
        ).pack(side="right")

        # Zone de logs
        self.log_text = Text(
            card,
            bg="#0d1117",
            fg="#f0f6fc",
            insertbackground="#f0f6fc",
            font=("Consolas", 9),
            relief="flat",
            borderwidth=0,
            wrap="none",
            state=DISABLED,
        )
        self.log_text.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        # Scrollbar
        scroll = Scrollbar(
            self.log_text,
            command=self.log_text.yview,
            bg="#161b22",
            troughcolor="#0d1117",
            borderwidth=0,
        )
        self.log_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

        # Tags de couleur
        self.log_text.tag_configure("red", foreground="#f85149")
        self.log_text.tag_configure("green", foreground="#3fb950")
        self.log_text.tag_configure("yellow", foreground="#d29922")

    def _build_results_tab(self, notebook):
        """Onglet des résultats avec style moderne."""
        res = Frame(notebook, bg="#0d1117")
        notebook.add(res, text="📊 Résultats")

        # --- Card : Trouvés ---
        card1 = Frame(res, bg="#161b22", relief="flat")
        card1.pack(fill="x", padx=4, pady=(6, 3))

        Label(
            card1,
            text="✅ Noms disponibles",
            font=("Segoe UI", 11, "bold"),
            bg="#161b22",
            fg="#3fb950",
        ).pack(anchor="w", padx=16, pady=(12, 8))

        self.found_box = Text(
            card1,
            height=6,
            bg="#0d1117",
            fg="#3fb950",
            font=("Consolas", 9),
            relief="flat",
            borderwidth=0,
            wrap="none",
            state=DISABLED,
        )
        self.found_box.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        # --- Card : Pris ---
        card2 = Frame(res, bg="#161b22", relief="flat")
        card2.pack(fill="x", padx=4, pady=(3, 6))

        Label(
            card2,
            text="❌ Derniers pris (50 max)",
            font=("Segoe UI", 11, "bold"),
            bg="#161b22",
            fg="#f85149",
        ).pack(anchor="w", padx=16, pady=(12, 8))

        self.taken_box = Text(
            card2,
            height=6,
            bg="#0d1117",
            fg="#f85149",
            font=("Consolas", 9),
            relief="flat",
            borderwidth=0,
            wrap="none",
            state=DISABLED,
        )
        self.taken_box.pack(fill="both", expand=True, padx=16, pady=(0, 12))

    # --- Méthodes de l'interface (callbacks pour le thread) ---

    def log(self, msg, color="white"):
        """Ajoute un message dans les logs (thread-safe)."""
        self.root.after(0, self._log, msg, color)

    def _log(self, msg, color):
        """Ajoute un message dans les logs (UI thread)."""
        self.log_text.config(state=NORMAL)
        self.log_text.insert(END, msg + "\n", color)

        # Limiter à MAX_LOG_LINES
        if int(self.log_text.index("end-1c").split(".")[0]) > MAX_LOG_LINES:
            self.log_text.delete(1.0, 2.0)

        self.log_text.see(END)
        self.log_text.config(state=DISABLED)

    def clear_log(self):
        """Efface les logs."""
        self.log_text.config(state=NORMAL)
        self.log_text.delete(1.0, END)
        self.log_text.config(state=DISABLED)

    def add_taken(self, name):
        """Ajoute un nom pris à la queue (thread-safe)."""
        self.taken_queue.append(name)
        self.root.after(0, self._update_taken)

    def _update_taken(self):
        """Met à jour l'affichage des noms pris (UI thread)."""
        self.taken_box.config(state=NORMAL)
        self.taken_box.delete(1.0, END)
        for n in reversed(self.taken_queue):
            self.taken_box.insert(END, n + "\n")
        self.taken_box.see(END)
        self.taken_box.config(state=DISABLED)

    def save_valid(self, name):
        """Sauvegarde un nom disponible (thread-safe)."""
        self.valid_buffer.append(name)
        if len(self.valid_buffer) >= self.BUFFER_SIZE:
            self._flush_valid_buffer()
        self.root.after(0, self._show_found, name)

    def _flush_valid_buffer(self):
        """Vide le buffer d'écriture dans valid.txt."""
        if self.valid_buffer:
            with open(self.valid_file, "a") as f:
                f.write("\n".join(self.valid_buffer) + "\n")
            self.valid_buffer.clear()

    def _show_found(self, name):
        """Affiche un nom disponible (UI thread)."""
        self.found_box.config(state=NORMAL)
        self.found_box.insert(END, name + "\n")
        self.found_box.see(END)
        self.found_box.config(state=DISABLED)
        if self.sniper:
            self.avail_lbl.config(text=str(self.sniper.available))

    def load_valid_usernames(self):
        """Charge les noms déjà trouvés depuis valid.txt."""
        if os.path.exists(self.valid_file):
            with open(self.valid_file) as f:
                names = f.read().splitlines()
            self.found_box.config(state=NORMAL)
            self.found_box.insert(END, "\n".join(names) + "\n")
            self.found_box.config(state=DISABLED)

    def update_checked(self, count):
        """Met à jour le compteur de vérifiés (thread-safe)."""
        self.root.after(0, lambda: self.checked_lbl.config(text=str(count)))

    def update_status(self, text):
        """Met à jour le statut (thread-safe)."""
        self.root.after(0, lambda: self.status_lbl.config(text=text))

    # --- Gestion des proxies (thread-safe) ---

    def load_proxies(self, from_file=False):
        """Charge les proxies depuis le texte ou le fichier."""
        if from_file and os.path.exists(self.proxies_file):
            with open(self.proxies_file) as f:
                self.proxy_text.delete(1.0, END)
                self.proxy_text.insert(END, f.read())

        raw_lines = self.proxy_text.get(1.0, END).splitlines()
        with self.proxy_lock:
            self.proxy_list = []
            for line in raw_lines:
                p = sanitize_proxy(line)
                if p:
                    self.proxy_list.append(p)
            self.proxy_index = -1

        self.proxy_cnt.config(text=f"{len(self.proxy_list)} chargés")

    def load_proxies_from_file(self):
        """Charge les proxies depuis proxies.txt."""
        self.load_proxies(from_file=True)
        self.log(f"📂 Chargé {len(self.proxy_list)} proxies.")

    def save_proxies_to_file(self):
        """Sauvegarde les proxies dans proxies.txt."""
        self.load_proxies(from_file=False)
        with self.proxy_lock:
            proxies = self.proxy_list.copy()
        with open(self.proxies_file, "w") as f:
            for p in proxies:
                f.write(p + "\n")
        self.log(f"💾 Sauvé {len(proxies)} proxies dans {self.proxies_file}")

    def get_next_proxy(self):
        """Retourne le prochain proxy en round-robin (thread-safe)."""
        with self.proxy_lock:
            if not self.proxy_list:
                return None
            self.proxy_index = (self.proxy_index + 1) % len(self.proxy_list)
            return self.proxy_list[self.proxy_index]

    def remove_proxy(self, proxy_url):
        """Supprime un proxy mort (thread-safe)."""
        with self.proxy_lock:
            if proxy_url in self.proxy_list:
                self.proxy_list.remove(proxy_url)
                self.log(f"🗑️ Proxy mort supprimé : {proxy_url}", "yellow")
                self.root.after(0, self._refresh_proxy_display)

    def _refresh_proxy_display(self):
        """Rafraîchit l'affichage des proxies (UI thread)."""
        with self.proxy_lock:
            proxies = self.proxy_list.copy()
        self.proxy_text.delete(1.0, END)
        self.proxy_text.insert(END, "\n".join(proxies))
        self.proxy_cnt.config(text=f"{len(proxies)} chargés")

    # --- Start / Stop ---

    def start_sniper(self):
        """Démarre le sniper."""
        # Validation du délai
        try:
            delay = float(self.delay_var.get())
            if delay < 0:
                raise ValueError
        except:
            messagebox.showerror("Erreur", "❌ Délai invalide (nombre positif requis)")
            return

        # Validation de la longueur
        try:
            length = int(self.length_var.get())
            if not 1 <= length <= 32:
                raise ValueError
        except:
            messagebox.showerror("Erreur", "❌ Longueur invalide (1-32)")
            return

        # Sauvegarde de la config
        self.config.update({
            "delay": delay,
            "length": length,
            "webhook": self.webhook_var.get().strip(),
            "no_verify": self.no_verify_var.get(),
            "zero_delay": self.zero_delay_var.get(),
        })
        save_config(self.config)

        # Chargement des proxies
        self.load_proxies(from_file=False)

        # Mise à jour de l'UI
        self.start_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)
        self.status_lbl.config(text="En cours...")
        self.checked_lbl.config(text="0")
        self.avail_lbl.config(text="0")

        # Démarrage du thread
        self.sniper = SniperThread(self, self.config)
        self.sniper.start()

    def stop_sniper(self):
        """Arrête le sniper."""
        if self.sniper:
            self.sniper.stop()
        self.start_btn.config(state=NORMAL)
        self.stop_btn.config(state=DISABLED)
        self.status_lbl.config(text="Arrêté")

    def on_close(self):
        """Gère la fermeture de l'application."""
        if self.sniper:
            self.sniper.stop()
        self._flush_valid_buffer()
        save_config(self.config)
        self.root.destroy()
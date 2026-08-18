# cry4snipe
cry4snipe – Username Sniper pour Discord
Sniping ultra‑rapide de noms d’utilisateur Discord, avec gestion avancée des proxies, backoff intelligent et interface moderne.

https://img.shields.io/badge/Python-3.8%252B-blue
https://img.shields.io/badge/Licence-MIT-green
https://img.shields.io/badge/GUI-Tkinter-orange
https://img.shields.io/badge/D%C3%A9pendances-Requests-lightgrey

📌 À propos
cry4snipe est un outil de sniping de noms d’utilisateur Discord. Il vérifie automatiquement des combinaisons aléatoires de caractères pour détecter les noms disponibles, et les sauvegarde dès qu’ils sont libres.

Le projet a été entièrement refactoré pour offrir :

une architecture modulaire et maintenable,

une gestion robuste des erreurs et des proxies,

des performances optimisées (buffer, backoff, logs limités),

une interface graphique moderne (thème sombre GitHub Dark).

✨ Fonctionnalités
Fonctionnalité	Description
Sniping automatique	Génération aléatoire de noms selon la longueur choisie, vérification via l’API Discord.
Double API	Alterne entre les endpoints username-attempt-unauthed et register pour éviter les rate‑limits.
Gestion intelligente des proxies	Rotation round‑robin, suppression automatique des proxies morts, test en parallèle avant utilisation.
Backoff exponentiel	En cas de rate‑limit (HTTP 429), le script attend de manière progressive (1s, 2s, 4s…) avant de réessayer.
Buffer d’écriture	Les noms disponibles sont regroupés (par défaut 10) avant d’être écrits dans valid.txt, réduisant les I/O.
Limitation des logs	La console de logs est limitée à 1000 lignes pour éviter les fuites mémoire.
Webhook Discord	Envoie une notification avec embed lorsqu’un nom est disponible ou déjà pris.
Interface moderne	Thème sombre (couleurs GitHub Dark), statistiques en grand format, onglets séparés.
Test de proxies intégré	Un bouton permet de tester tous les proxies en parallèle et de ne garder que les fonctionnels.
Récupération automatique	Récupère 200 proxies frais depuis ProxyScrape et les teste en une seule action.
📦 Installation
Prérequis
Python 3.8 ou supérieur

Pip (gestionnaire de paquets)

Étapes
bash
# 1. Cloner le dépôt
git clone https://github.com/votre-utilisateur/cry4snipe.git
cd cry4snipe

# 2. Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate   # Linux/Mac
# ou
venv\Scripts\activate      # Windows

# 3. Installer les dépendances
pip install -r requirements.txt
Dépendances
requests – pour les appels HTTP

tkinter – interface graphique (inclus avec Python)

Le fichier requirements.txt contient :

text
requests>=2.28.0
🚀 Utilisation
Lancement
bash
python cry4snipe.py
Interface
L’application se compose de 4 onglets :

⚙️ Config & Contrôle

Délai entre chaque tentative (secondes).

Longueur du nom à générer (1–32 caractères).

URL du webhook Discord (optionnelle).

Options avancées : désactivation SSL, délai nul avec proxies.

Boutons START / STOP.

Statistiques en direct : nombres de vérifiés et de disponibles.

🌐 Proxies

Saisie manuelle des proxies (un par ligne).

Bouton Charger (depuis proxies.txt).

Bouton Sauvegarder (dans proxies.txt).

Bouton Tester les proxies (test parallèle, ne garde que les valides).

Bouton Récupérer frais (200) (télécharge 200 proxies depuis ProxyScrape et les teste automatiquement).

📋 Logs

Console de logs colorés (vert = disponible, rouge = pris, jaune = avertissement).

Bouton Effacer pour vider la console.

📊 Résultats

Liste des noms disponibles sauvegardés dans valid.txt.

Liste des 50 derniers noms pris (utile pour suivre les tentatives).

⚙️ Configuration
Fichier config.json
À la première exécution, un fichier config.json est créé avec les valeurs par défaut :

json
{
    "delay": 5.0,
    "length": 5,
    "webhook": "",
    "no_verify": false,
    "zero_delay": false,
    "proxy_file": "proxies.txt",
    "valid_file": "valid.txt",
    "config_file": "config.json"
}
delay : délai entre deux requêtes (en secondes).

length : longueur du nom généré.

webhook : URL du webhook Discord (vide = désactivé).

no_verify : désactive la vérification SSL (utile pour certains proxies).

zero_delay : met le délai à 0 si des proxies sont chargés (à utiliser avec prudence).

proxy_file / valid_file : noms des fichiers de stockage.

🌐 Gestion des proxies
Formats acceptés
ip:port → sera automatiquement transformé en http://ip:port

http://ip:port

https://ip:port

Les proxies socks sont ignorés par défaut.

Recommandations
Utilisez au moins 100 proxies pour un sniping efficace.

Privilégiez les SOCKS5 (plus rapides et stables) si vous avez la bibliothèque pysocks.

Testez vos proxies régulièrement (bouton Tester les proxies) car les listes publiques expirent vite.

🖼️ Captures d’écran
(À ajouter après les captures – exemple de commande pour générer des images)

bash
# Si vous utilisez scrot (Linux) ou tout autre outil
scrot -u -e 'mv $f screenshots/'
❓ Dépannage
Problème	Solution
Tous les proxies sont morts	Utilisez le bouton Récupérer frais (200) pour obtenir une nouvelle liste.
Aucune connexion établie	Vérifiez votre connexion Internet, ou augmentez le timeout dans constants.py.
Rate limit (429)	Le script gère automatiquement le backoff, patientez.
La fenêtre ne s’ouvre pas	Vérifiez que tkinter est installé : python -m tkinter.
Erreur d’import requests	Installez la dépendance : pip install requests.
Le sniper ne trouve rien	Essayez de réduire le délai ou d’augmenter le nombre de proxies.
🔒 Sécurité et limites
Ce script est fourni à titre éducatif. L’utilisation massive peut violer les conditions d’utilisation de Discord.

Les proxies gratuits sont publics et souvent surchargés : ne les utilisez pas pour des données sensibles.

Le sniping de noms peut être interprété comme du spam par Discord → utilisez des délais raisonnables.

🤝 Contribuer
Les contributions sont les bienvenues ! Pour proposer une amélioration :

Fork le projet.

Créez votre branche (git checkout -b feature/amazing-feature).

Committez vos changements (git commit -m 'Ajout d’une fonctionnalité').

Pushez (git push origin feature/amazing-feature).

Ouvrez une Pull Request.

📄 Licence
Ce projet est distribué sous la licence MIT. Voir le fichier LICENSE pour plus d’informations.

🙏 Remerciements
OnajLikezz – pour l’idée initiale et le script de base.

La communauté Python pour les bibliothèques requests et tkinter.

GitHub et les dépôts de proxies gratuits.

Cry4snipe – Snip like a pro, stay undetected. ❄️

# cry4snipe
# ❄️ cry4snipe

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Downloads](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

> Sniping de noms d'utilisateur Discord, simple et efficace.

```python
# Ce que fait cry4snipe en une ligne
$ python cry4snipe.py
# → Interface graphique
# → Génération de noms aléatoires
# → Vérification automatique via l'API Discord
# → Sauvegarde des noms disponibles dans valid.txt
cry4snipe est un outil qui génère automatiquement des combinaisons de caractères et vérifie si elles sont disponibles comme nom d'utilisateur sur Discord. Quand un nom est libre, il le sauvegarde et t'envoie une notification.

Installation
bash
git clone https://github.com/tonpseudo/cry4snipe.git
cd cry4snipe
pip install -r requirements.txt
Utilisation
bash
python cry4snipe.py
L'interface s'ouvre. Tu choisis :

le délai entre chaque tentative

la longueur du nom à générer

tes proxies (optionnel)

Puis tu cliques sur START.

Fonctionnalités
Génération aléatoire de noms (longueur personnalisable)

Vérification via l'API Discord

Gestion des proxies (round-robin, suppression automatique des morts)

Backoff automatique en cas de rate-limit

Webhook Discord pour les alertes

Interface graphique moderne (thème sombre)

Test de proxies intégré

Récupération automatique de proxies frais

Proxies
Les proxies gratuits meurent vite. Le bouton "Récupérer frais (200)" va chercher des proxies récents et les teste automatiquement.

Format accepté : ip:port ou http://ip:port

Fichiers
proxies.txt — liste des proxies

valid.txt — noms trouvés

config.json — réglages sauvegardés

Dépendances
requests — pour les appels HTTP

tkinter — pour l'interface (inclus avec Python)

License
MIT — fais ce que tu veux avec.

Snip bien. ❄️

"""Constantes de configuration du moteur de scoring ScalBnB.

Tout ce qui est susceptible d'être ajusté sans toucher à la logique de calcul
(seuils, libellés, emojis) vit ici plutôt que dispersé dans le code métier.
"""

from typing import Dict, List, Optional, Tuple

# Colonnes d'équipements comparées : (colonne du logement, colonne "présent chez les tops du segment")
EQUIPS: List[Tuple[str, str]] = [
    ("Wifi_x", "Wifi_y"),
    ("kitchen_x", "kitchen_y"),
    ("has_washer_x", "has_washer_y"),
    ("air conditioning_x", "air conditioning_y"),
    ("parking_gratuit_x", "parking_gratuit_y"),
]

# Seuil minimum de mentions (%) dans les avis pour déclencher une alerte sur un thème
SEUIL_ALERTE_REVIEWS = 10

REVIEW_THEMES: Dict[str, dict] = {
    "proprete": {
        "label": "Améliorer la propreté du logement",
        "keywords": [
            "sale", "dirty", "poussière", "poussiere", "dust", "moisissure",
            "mold", "pas propre", "not clean", "ménage", "menage",
            "could be cleaner", "hygiène", "hygiene",
        ],
        "emoji": "🧹",
    },
    "bruit": {
        "label": "Réduire les nuisances sonores",
        "keywords": ["bruit", "bruyant", "noise", "noisy", "loud", "insonor", "soundproof"],
        "emoji": "🔇",
    },
    "confort_literie": {
        "label": "Améliorer le confort de la literie",
        "keywords": [
            "matelas", "mattress", "inconfort", "uncomfort", "mal dormi",
            "bad sleep", "hard bed", "lit dur", "sommeil",
        ],
        "emoji": "🛏️",
    },
    "temperature": {
        "label": "Améliorer la gestion de la température",
        "keywords": [
            "froid", "cold apartment", "pas de chauffage", "no heating",
            "trop chaud", "too hot", "pas de clim", "no air condition",
            "freezing", "gelé",
        ],
        "emoji": "🌡️",
    },
    "accueil": {
        "label": "Améliorer la communication et l'accueil",
        "keywords": [
            "pas répondu", "pas repondu", "no response", "hard to reach",
            "difficult to reach", "no reply", "sans réponse", "sans reponse",
            "late check", "retard arrivée", "attendre longtemps", "waited long",
        ],
        "emoji": "💬",
    },
}

# (seuil minimum, nom, emoji, couleur, nom du badge suivant) — parcouru du plus haut au plus bas seuil
BADGES: List[Tuple[int, str, str, str, Optional[str]]] = [
    (85, "Diamant", "🏆", "#B9F2FF", None),
    (70, "Or", "🥇", "#FFD700", "Diamant"),
    (50, "Argent", "🥈", "#C0C0C0", "Or"),
    (0, "Bronze", "🥉", "#CD7F32", "Argent"),
]

TIER_RANGES: Dict[str, Tuple[int, int]] = {
    "Diamant": (85, 100),
    "Or": (70, 85),
    "Argent": (50, 70),
    "Bronze": (0, 50),
}

# Actions proposées dans l'onglet Simulateur : (colonne recommandation, colonne cible, libellé affiché)
# NB : "recor_wifi" (sans le "d") correspond au nom de colonne tel qu'il existe dans master_final.csv.
# Je le garde identique pour ne pas casser la lecture du CSV — à corriger côté pipeline si besoin,
# pas ici.
RECO_MAP: List[Tuple[str, str, str]] = [
    ("recor_wifi", "Wifi_x", "Ajouter le Wifi"),
    ("reco_kitchen", "kitchen_x", "Ajouter une cuisine équipée"),
    ("reco_washer", "has_washer_x", "Installer un lave-linge"),
    ("reco_ac", "air conditioning_x", "Installer la climatisation"),
    ("reco_parking", "parking_gratuit_x", "Proposer un parking gratuit"),
    ("reco_nuit", "minimum_nights_x", "Réduire le minimum de nuits"),
]

# Ordre de priorité utilisé pour choisir l'action mise en avant dans l'email mensuel
RECO_PRIORITES: List[Tuple[str, str]] = [
    ("recor_wifi", "Ajouter le Wifi"),
    ("reco_kitchen", "Ajouter une cuisine équipée"),
    ("reco_washer", "Installer un lave-linge"),
    ("reco_parking", "Proposer un parking gratuit"),
    ("reco_ac", "Installer la climatisation"),
    ("reco_nuit", "Réduire votre nombre de nuits minimum"),
]
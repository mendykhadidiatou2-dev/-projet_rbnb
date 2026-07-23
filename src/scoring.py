"""Calcul du score ScalBnB et attribution des badges de niveau.

Le score est composé de 4 sous-scores (équipements, occupation, avis, nuits
minimum) et vaut sur 100. Une seule fonction porte la formule (`compute_scores`,
vectorisée) ; `compute_score_single` la réutilise pour un logement isolé afin
de ne pas avoir deux implémentations du même calcul qui risquent de diverger
avec le temps.
"""

from typing import Optional, Tuple

import numpy as np
import pandas as pd

from src.config import BADGES, EQUIPS


def compute_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule les 4 sous-scores et le score final pour chaque ligne.

    Ajoute les colonnes score_equip, score_occ, score_rating, score_nights
    et score_scalbnb, et retourne le DataFrame modifié.
    """
    equip_earned = sum(df[x] * df[y] for x, y in EQUIPS)
    equip_max = sum(df[y] for _, y in EQUIPS)
    df["score_equip"] = np.where(equip_max > 0, equip_earned / equip_max, 1.0)

    df["score_occ"] = np.where(
        df["seuil"] > 0,
        np.minimum(df["estimated_occupancy_l365d"] / df["seuil"], 1.0),
        0.5,
    )

    df["score_rating"] = (df["review_scores_rating"].fillna(2.5) - 1.0) / 4.0

    df["score_nights"] = 1.0 - np.minimum(
        np.abs(df["minimum_nights_x"] - df["minimum_nights_y"].fillna(2.0)) / 5.0, 1.0
    )

    df["score_scalbnb"] = (
        df["score_equip"] * 30
        + df["score_occ"] * 30
        + df["score_rating"] * 25
        + df["score_nights"] * 15
    )
    return df


def compute_score_single(row: pd.Series) -> float:
    """Calcule le score ScalBnB pour un seul logement (ex: simulation d'amélioration).

    On repasse par `compute_scores` en enveloppant la ligne dans un DataFrame
    d'une seule ligne. Ça évite de dupliquer la formule, et .fillna() se
    comporte alors comme sur le dataset complet (un scalaire nu n'a pas
    cette méthode, ce qui obligeait l'ancienne version à un traitement à part).
    """
    single_row_df = pd.DataFrame([row])
    scored = compute_scores(single_row_df)
    return float(scored.iloc[0]["score_scalbnb"])


def get_badge(score: float) -> Tuple[str, str, str, Optional[str]]:
    """Retourne (nom_badge, emoji, couleur, nom_du_badge_suivant) pour un score donné.

    BADGES contient un seuil à 0, donc la boucle trouve toujours une
    correspondance : le retour par défaut n'est qu'un filet de sécurité.
    """
    for seuil, nom, emoji, couleur, prochain in BADGES:
        if score >= seuil:
            return nom, emoji, couleur, prochain
    return "Bronze", "🥉", "#CD7F32", "Argent"
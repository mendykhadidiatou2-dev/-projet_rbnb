"""Analyse des avis voyageurs pré-calculée (reviews_analysis.csv)."""

from typing import List, Tuple

import pandas as pd

from src.config import REVIEW_THEMES, SEUIL_ALERTE_REVIEWS


def get_review_alerts(df_reviews: pd.DataFrame, listing_id: int) -> List[Tuple[str, str, float, int]]:
    """Renvoie les thèmes qui dépassent le seuil d'alerte pour un logement donné.

    Chaque alerte est un tuple (emoji, libellé, % de mentions, nombre d'avis
    concernés), triée par pourcentage décroissant. Liste vide si le logement
    n'a pas d'avis ou si aucun thème ne dépasse le seuil.
    """
    if listing_id not in df_reviews.index:
        return []

    review_row = df_reviews.loc[listing_id]
    alertes = []
    for theme, config in REVIEW_THEMES.items():
        pct = review_row[f"pct_{theme}"]
        if pct >= SEUIL_ALERTE_REVIEWS:
            alertes.append((config["emoji"], config["label"], pct, int(review_row[f"neg_{theme}"])))

    return sorted(alertes, key=lambda alerte: -alerte[2])


def get_review_count(df_reviews: pd.DataFrame, listing_id: int) -> int:
    """Nombre d'avis analysés pour un logement (0 si aucun avis disponible)."""
    if listing_id not in df_reviews.index:
        return 0
    return int(df_reviews.loc[listing_id, "nb_reviews"])
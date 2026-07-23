"""Positionnement d'un logement dans le classement de son quartier."""

from typing import Tuple

import pandas as pd


def get_neighborhood_ranking(
    df: pd.DataFrame, listing_id: int, quartier: str
) -> Tuple[int, int, pd.DataFrame]:
    """Classe un logement parmi les autres logements du même quartier.

    Retourne (rang, nombre total de logements comparables, top 5 du quartier).
    Le top 5 tronque l'ID à ses 4 derniers chiffres pour l'affichage.
    """
    voisins = df[df["neighbourhood_cleansed"] == quartier].copy()
    voisins = voisins.sort_values("score_scalbnb", ascending=False).reset_index(drop=True)
    total = len(voisins)

    idx = voisins[voisins["id"] == listing_id].index
    rang = int(idx[0]) + 1 if len(idx) > 0 else total

    top5 = voisins.head(5)[["id", "score_scalbnb", "room_type", "accommodates"]].copy()
    top5.columns = ["ID", "Score", "Type", "Capacité"]
    top5.insert(0, "Rang", range(1, len(top5) + 1))
    top5["Score"] = top5["Score"].round(1)
    top5["ID"] = top5["ID"].apply(lambda x: f"...{str(x)[-4:]}")

    return rang, total, top5
"""Tests de non-régression sur src.scoring.

Lancer avec : pytest tests/
"""

import pandas as pd

from src.scoring import compute_score_single, compute_scores, get_badge


def _sample_row() -> pd.Series:
    """Logement fictif entièrement équipé, occupation et avis au maximum."""
    return pd.Series({
        "Wifi_x": 1, "Wifi_y": 1,
        "kitchen_x": 1, "kitchen_y": 1,
        "has_washer_x": 1, "has_washer_y": 1,
        "air conditioning_x": 1, "air conditioning_y": 1,
        "parking_gratuit_x": 1, "parking_gratuit_y": 1,
        "estimated_occupancy_l365d": 300,
        "seuil": 300,
        "review_scores_rating": 5.0,
        "minimum_nights_x": 2,
        "minimum_nights_y": 2,
    })


def test_score_maxed_out_is_100():
    assert compute_score_single(_sample_row()) == 100.0


def test_missing_equipment_lowers_score():
    full_score = compute_score_single(_sample_row())

    reduced = _sample_row()
    reduced["has_washer_x"] = 0

    assert compute_score_single(reduced) < full_score


def test_get_badge_thresholds():
    assert get_badge(90)[0] == "Diamant"
    assert get_badge(75)[0] == "Or"
    assert get_badge(55)[0] == "Argent"
    assert get_badge(10)[0] == "Bronze"


def test_compute_scores_matches_compute_score_single():
    """Les deux fonctions doivent renvoyer le même score pour le même logement."""
    df = pd.DataFrame([_sample_row(), _sample_row()])
    scored_df = compute_scores(df.copy())

    single_score = compute_score_single(_sample_row())

    assert abs(scored_df.iloc[0]["score_scalbnb"] - single_score) < 1e-9
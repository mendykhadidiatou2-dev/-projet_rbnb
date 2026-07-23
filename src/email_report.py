"""Construction de l'aperçu HTML de l'email de rapport mensuel envoyé à l'hôte."""

from datetime import datetime
from typing import List, Optional, Tuple

import pandas as pd

from src.config import TIER_RANGES


def get_top_priority_action(logement: pd.Series, reco_priorites: List[Tuple[str, str]]) -> Optional[str]:
    """Renvoie le libellé de la première action de recommandation présente pour ce logement.

    reco_priorites est déjà ordonné par priorité (voir config.RECO_PRIORITES) :
    on renvoie la première correspondance trouvée.
    """
    for col, label in reco_priorites:
        if pd.notna(logement.get(col)):
            return label
    return None


def _badge_section(score: float, badge_prochain: Optional[str]) -> str:
    if not badge_prochain:
        return ""
    pts = TIER_RANGES[badge_prochain][0] - score
    return f"""
    <div style="background:#d4edda; padding:12px; border-radius:8px; margin:12px 0;">
        <p style="margin:0;">🚀 <b>Objectif du mois</b> : Plus que <b>{pts:.0f} points</b>
        pour atteindre le niveau <b>{badge_prochain}</b> !</p>
    </div>"""


def _action_section(top_action: Optional[str]) -> str:
    if not top_action:
        return ""
    return f"""
    <div style="background:#fff3cd; padding:12px; border-radius:8px; margin:12px 0;">
        <p style="margin:0;"><b>🎯 Action prioritaire ce mois-ci :</b></p>
        <p style="margin:4px 0 0 0;">{top_action}</p>
    </div>"""


def _reviews_section(alerts: List[Tuple[str, str, float, int]]) -> str:
    if not alerts:
        return ""
    items = "".join(f"<li>{emoji} {label} ({pct:.0f}% des avis)</li>" for emoji, label, pct, _ in alerts)
    return f"""
    <div style="background:#f8d7da; padding:12px; border-radius:8px; margin:12px 0;">
        <p style="margin:0 0 6px 0;"><b>💬 Retours voyageurs à traiter :</b></p>
        <ul style="margin:0; padding-left:20px;">{items}</ul>
    </div>"""


def build_monthly_email_html(
    score: float,
    badge_nom: str,
    badge_emoji: str,
    badge_prochain: Optional[str],
    rang: int,
    total_quartier: int,
    quartier: str,
    top_action: Optional[str],
    alerts: List[Tuple[str, str, float, int]],
) -> str:
    """Construit le HTML complet de l'email de rapport mensuel.

    Les blocs objectif / action prioritaire / avis à traiter sont chacun
    optionnels et ne s'affichent que si l'information existe, pour ne pas
    montrer de section vide à l'hôte.
    """
    mois = datetime.now().strftime("%B %Y").capitalize()

    return f"""
    <div style="border:2px solid #e0e0e0; border-radius:12px; padding:0;
                max-width:500px; margin:auto; font-family:Arial,sans-serif;
                overflow:hidden;">
        <div style="text-align:center; background:linear-gradient(135deg, #667eea, #764ba2);
                    color:white; padding:20px;">
            <h2 style="margin:0;">🏠 ScalBnB</h2>
            <p style="margin:4px 0 0 0; opacity:0.9;">Rapport Mensuel — {mois}</p>
        </div>
        <div style="padding:20px;">
            <div style="text-align:center; padding:16px 0;">
                <p style="font-size:48px; margin:0;">{badge_emoji}</p>
                <h1 style="margin:4px 0;">{score:.0f} / 100</h1>
                <p style="margin:0; color:#666;">Niveau <b>{badge_nom}</b></p>
            </div>
            <div style="background:#f8f9fa; padding:12px; border-radius:8px; margin:12px 0;">
                <p style="margin:0;">📍 <b>Votre position</b> :
                {rang}e sur {total_quartier} dans <b>{quartier}</b></p>
            </div>
            {_badge_section(score, badge_prochain)}
            {_action_section(top_action)}
            {_reviews_section(alerts)}
            <div style="text-align:center; margin-top:20px;">
                <a href="#" style="background:linear-gradient(135deg,#667eea,#764ba2);
                   color:white; padding:12px 24px; border-radius:8px;
                   text-decoration:none; font-weight:bold;">
                    Voir mon tableau de bord complet
                </a>
            </div>
            <div style="text-align:center; color:#aaa; font-size:11px;
                        margin-top:24px; padding-top:16px; border-top:1px solid #eee;">
                <p>Cet email est envoyé maximum 2 fois par mois.</p>
                <p><a href="#" style="color:#aaa;">Se désinscrire</a> |
                   <a href="#" style="color:#aaa;">Gérer mes préférences</a></p>
            </div>
        </div>
    </div>
    """
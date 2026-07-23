"""Application Streamlit ScalBnB : audit d'annonces Airbnb à Bordeaux Métropole.

Toute la logique de calcul (score, classement, avis, email) vit dans src/.
Ce fichier ne fait que l'orchestration de l'interface.
"""

import pandas as pd
import streamlit as st

from src.config import RECO_MAP, RECO_PRIORITES, TIER_RANGES
from src.data_loader import load_data, load_reviews_analysis
from src.email_report import build_monthly_email_html, get_top_priority_action
from src.ranking import get_neighborhood_ranking
from src.reviews import get_review_alerts, get_review_count
from src.scoring import compute_score_single, compute_scores, get_badge

st.set_page_config(page_title="ScalBnB - Moteur d'Audit", page_icon="🏠", layout="centered")

df_master = compute_scores(load_data())
df_reviews = load_reviews_analysis()

st.title("🏠 ScalBnB Smart Insights")
st.subheader("Le moteur d'IA pour booster le remplissage de votre Airbnb")
st.write("---")

st.sidebar.header("Tableau de Bord")
st.sidebar.write("Utilisez cet outil pour auditer une annonce à Bordeaux.")

id_saisi = st.number_input(
    "Entrez l'identifiant (ID) du logement à analyser :",
    min_value=0, step=1, value=0,
)

if id_saisi == 0:
    st.info(
        "👋 Bienvenue sur l'application de démo ScalBnB ! "
        "Veuillez saisir un identifiant de logement ci-dessus "
        "pour lancer l'audit automatique de l'IA."
    )
    st.stop()

if id_saisi not in df_master["id"].values:
    st.error(
        "❌ Cet identifiant de logement n'existe pas dans la base de données "
        "de Bordeaux. Veuillez vérifier votre saisie."
    )
    st.stop()

logement = df_master[df_master["id"] == id_saisi].iloc[0]
quartier = logement["neighbourhood_cleansed"]
groupe = logement["classement"]
reco = logement["recommandation_finale"]
score = logement["score_scalbnb"]

badge_nom, badge_emoji, badge_couleur, badge_prochain = get_badge(score)
rang, total_quartier, top5 = get_neighborhood_ranking(df_master, id_saisi, quartier)

# ========================= SCORE CARD (toujours visible) =========================
col_badge, col_score, col_rang = st.columns([1, 2, 1])

with col_badge:
    st.markdown(f"### {badge_emoji} {badge_nom}")

with col_score:
    st.metric("Score ScalBnB", f"{score:.0f} / 100")
    if badge_prochain:
        tier_min, tier_max = TIER_RANGES[badge_nom]
        progression = (score - tier_min) / (tier_max - tier_min)
        st.progress(min(max(progression, 0.0), 1.0))
        pts_restants = TIER_RANGES[badge_prochain][0] - score
        st.caption(f"Plus que **{pts_restants:.0f} pts** pour le niveau {badge_prochain}")
    else:
        st.progress(1.0)
        st.caption("Niveau maximum atteint !")

with col_rang:
    percentile_card = max(round(rang / total_quartier * 100), 1)
    st.metric(f"Rang — {quartier[:20]}", f"{rang}e / {total_quartier}")
    st.caption(f"Top {percentile_card}%")

st.write("---")

tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Diagnostic", "🎯 Simulateur", "🏅 Classement", "📧 Email Rapport"]
)

# ================================ ONGLET 1 : DIAGNOSTIC ================================
with tab1:
    st.write(f"### 📍 Analyse locale du secteur : **{quartier}**")

    if groupe == 1:
        st.success("🏆 **Profil : Logement Champion (Top)**")
        st.balloons()
        st.write(
            "Félicitations ! Votre logement correspond déjà au profil des "
            "meilleurs de votre secteur concurrentiel. Continuez ainsi !"
        )
    elif groupe == -1:
        st.warning("⚠️ **Profil : Analyse Limitée**")
        st.write(
            "Il n'y a pas assez de logements comparables (moins de 10) dans "
            "votre secteur géographique pour établir un diagnostic statistique fiable."
        )
    else:
        equip_deja_ok = (
            pd.isna(reco) or reco.strip() == ""
            or "correspond déjà" in str(reco)
            or "possède déjà les standards" in str(reco)
        )
        if equip_deja_ok:
            st.warning("📉 **Profil : Standard / Flop (Équipements OK)**")
            st.write("### 📋 Votre Plan d'Action Personnalisé :")
            st.info(
                "✨ Votre logement possède déjà tous les standards matériels et "
                "logistiques des leaders de votre quartier. L'absence de réservations "
                "ne vient pas de vos équipements : nous vous conseillons d'optimiser "
                "en priorité la qualité de vos photos ou de réajuster vos tarifs."
            )
        else:
            st.error("📉 **Profil : Optimisation Requise (Standard/Flop)**")

            col1, col2 = st.columns(2)
            with col1:
                valeur_occ = logement.get("estimated_occupancy_l365d", 0.152)
                occ_actuel = round(valeur_occ * 100, 1) if valeur_occ <= 1.0 else round(valeur_occ, 1)
                st.metric("📈 Votre Taux d'Occupation", f"{occ_actuel} %", delta="-35% vs les Tops")
            with col2:
                nb_voisins = int(logement.get("taille_groupe", 12))
                st.metric("👥 Logements comparés", value=nb_voisins)

            st.write("---")
            st.write("### 📋 Votre Plan d'Action Personnalisé :")
            for phrase in str(reco).split("\n"):
                phrase = phrase.strip()
                if phrase and "correspond déjà" not in phrase and "possède déjà les standards" not in phrase:
                    st.markdown(f"**💡 {phrase}**")

        st.write("---")
        st.write("### 📐 Décomposition du Score ScalBnB")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Équipements", f"{logement['score_equip'] * 30:.0f} / 30")
        c2.metric("Occupation", f"{logement['score_occ'] * 30:.0f} / 30")
        c3.metric("Avis Clients", f"{logement['score_rating'] * 25:.0f} / 25")
        c4.metric("Min. Nuits", f"{logement['score_nights'] * 15:.0f} / 15")

    st.write("---")
    st.write("### 💬 Analyse des Retours Voyageurs")
    nb_rev = get_review_count(df_reviews, id_saisi)

    if nb_rev > 0:
        st.caption(f"Basé sur l'analyse de **{nb_rev} avis** de voyageurs.")
        alertes = get_review_alerts(df_reviews, id_saisi)
        if alertes:
            st.warning(f"⚠️ **{len(alertes)} point(s) d'attention** détecté(s) dans les commentaires de vos voyageurs :")
            for emoji, label, pct, count in alertes:
                st.markdown(f"**{emoji} {label}** — mentionné dans **{pct:.0f}%** des avis ({count}/{nb_rev})")
        else:
            st.success("✅ Aucun problème récurrent détecté dans les avis de vos voyageurs. Continuez ainsi !")
    else:
        st.info(
            "📭 Aucun avis voyageur disponible pour ce logement. "
            "Les recommandations ci-dessus sont basées sur les équipements et la configuration de votre annonce."
        )

# ================================ ONGLET 2 : SIMULATEUR ================================
with tab2:
    if groupe == -1:
        st.warning("⚠️ Pas assez de logements comparables dans votre secteur pour proposer des simulations fiables.")
    else:
        st.write("### 🎯 Simulateur d'Améliorations")
        st.caption("Cochez les actions que vous comptez réaliser pour voir l'impact sur votre score en temps réel.")

        simulated = logement.copy()
        has_any_reco = False
        actions_cochees = 0

        for reco_col, x_col, label in RECO_MAP:
            if pd.isna(logement.get(reco_col)):
                continue
            has_any_reco = True

            test_row = logement.copy()
            if reco_col == "reco_nuit":
                test_row["minimum_nights_x"] = test_row["minimum_nights_y"]
            else:
                test_row[x_col] = 1
            gain = compute_score_single(test_row) - score

            checked = st.checkbox(f"{label} *(+{gain:.1f} pts)*", key=f"sim_{reco_col}_{id_saisi}")
            if checked:
                actions_cochees += 1
                if reco_col == "reco_nuit":
                    simulated["minimum_nights_x"] = simulated["minimum_nights_y"]
                else:
                    simulated[x_col] = 1

        if not has_any_reco:
            st.success("✨ Votre logement possède déjà tous les équipements recommandés pour votre secteur. Bravo !")
        else:
            st.write("---")
            new_score = compute_score_single(simulated)
            delta = new_score - score
            new_badge_nom, new_badge_emoji, _, _ = get_badge(new_score)

            col_avant, col_apres = st.columns(2)
            with col_avant:
                st.metric("Score Actuel", f"{score:.0f} / 100")
                st.markdown(f"Niveau : {badge_emoji} **{badge_nom}**")
            with col_apres:
                st.metric("Score Simulé", f"{new_score:.0f} / 100", delta=f"+{delta:.0f} pts" if delta > 0 else None)
                st.markdown(f"Niveau : {new_badge_emoji} **{new_badge_nom}**")

            if new_badge_nom != badge_nom and delta > 0:
                st.success(f"🎉 En appliquant ces {actions_cochees} action(s), vous passeriez au niveau **{new_badge_nom}** !")

# ================================ ONGLET 3 : CLASSEMENT ================================
with tab3:
    st.write(f"### 🏅 Classement dans **{quartier}**")
    percentile = max(round(rang / total_quartier * 100), 1)
    st.metric(
        label=f"Votre position parmi {total_quartier} logements",
        value=f"{rang}e sur {total_quartier}",
        delta=f"Top {percentile}%",
    )

    if groupe == -1:
        st.caption("⚠️ Attention : ce secteur contient peu de logements comparables, le classement est indicatif.")

    with st.expander("📋 Voir le Top 5 du quartier"):
        st.dataframe(top5, hide_index=True, use_container_width=True)

    st.write("#### Votre position sur l'échelle du quartier")
    position_norm = 1 - (rang / total_quartier)
    st.progress(min(max(position_norm, 0.0), 1.0))

    if percentile <= 25:
        st.success("Vous faites partie des meilleurs de votre quartier !")
    elif percentile <= 50:
        st.info("Vous êtes dans la moitié supérieure. Continuez vos efforts !")
    else:
        st.warning("Il y a une marge de progression significative dans votre quartier.")

# ================================ ONGLET 4 : EMAIL RAPPORT ================================
with tab4:
    st.write("### 📧 Aperçu du Rapport Mensuel ScalBnB")
    st.caption("Voici à quoi ressemblerait l'email que vous recevriez chaque mois.")

    top_action = get_top_priority_action(logement, RECO_PRIORITES)
    alertes_email = get_review_alerts(df_reviews, id_saisi)

    email_html = build_monthly_email_html(
        score=score,
        badge_nom=badge_nom,
        badge_emoji=badge_emoji,
        badge_prochain=badge_prochain,
        rang=rang,
        total_quartier=total_quartier,
        quartier=quartier,
        top_action=top_action,
        alerts=alertes_email,
    )
    st.markdown(email_html, unsafe_allow_html=True)

    st.write("")
    with st.expander("📖 Stratégie anti-fatigue : pourquoi seulement 2 emails/mois ?"):
        st.markdown(
            """
            **Règle 1 — Rapport mensuel** (1er du mois) :
            Un seul email récapitulatif avec votre score, votre badge, votre position
            dans le quartier et votre action prioritaire.

            **Règle 2 — Rappel conditionnel** (15 du mois) :
            Envoyé **uniquement si** :
            - Vous êtes à moins de 5 points du niveau supérieur
            - OU votre score a évolué depuis le dernier rapport

            **Règle 3 — Pause automatique** :
            Si vous maintenez le niveau Diamant pendant **3 mois consécutifs**,
            les emails passent automatiquement à **1 par trimestre**.

            **Résultat** : pas de spam, uniquement des informations
            actionnables qui vous donnent envie de revenir.
            """
        )
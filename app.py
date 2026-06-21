import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# CONFIGURATION DE LA PAGE WEB
st.set_page_config(page_title="ScalBnB - Moteur d'Audit", page_icon="🏠", layout="centered")


# =============================================================
# FONCTIONS UTILITAIRES
# =============================================================

@st.cache_data
def load_data():
    df = pd.read_csv("data/master_final.csv")
    return df


REVIEW_THEMES = {
    'proprete': {
        'label': "Améliorer la propreté du logement",
        'keywords': ['sale', 'dirty', 'poussière', 'poussiere', 'dust', 'moisissure',
                     'mold', 'pas propre', 'not clean', 'ménage', 'menage',
                     'could be cleaner', 'hygiène', 'hygiene'],
        'emoji': '🧹',
    },
    'bruit': {
        'label': "Réduire les nuisances sonores",
        'keywords': ['bruit', 'bruyant', 'noise', 'noisy', 'loud', 'insonor', 'soundproof'],
        'emoji': '🔇',
    },
    'confort_literie': {
        'label': "Améliorer le confort de la literie",
        'keywords': ['matelas', 'mattress', 'inconfort', 'uncomfort', 'mal dormi',
                     'bad sleep', 'hard bed', 'lit dur', 'sommeil'],
        'emoji': '🛏️',
    },
    'temperature': {
        'label': "Améliorer la gestion de la température",
        'keywords': ['froid', 'cold apartment', 'pas de chauffage', 'no heating',
                     'trop chaud', 'too hot', 'pas de clim', 'no air condition',
                     'freezing', 'gelé'],
        'emoji': '🌡️',
    },
    'accueil': {
        'label': "Améliorer la communication et l'accueil",
        'keywords': ['pas répondu', 'pas repondu', 'no response', 'hard to reach',
                     'difficult to reach', 'no reply', 'sans réponse', 'sans reponse',
                     'late check', 'retard arrivée', 'attendre longtemps', 'waited long'],
        'emoji': '💬',
    },
}

SEUIL_ALERTE_REVIEWS = 10


@st.cache_data
def load_reviews_analysis():
    df = pd.read_csv("data/reviews_analysis.csv", index_col='listing_id')
    return df


EQUIPS = [
    ('Wifi_x', 'Wifi_y'),
    ('kitchen_x', 'kitchen_y'),
    ('has_washer_x', 'has_washer_y'),
    ('air conditioning_x', 'air conditioning_y'),
    ('parking_gratuit_x', 'parking_gratuit_y'),
]


@st.cache_data
def compute_all_scores(df):
    equip_earned = sum(df[x] * df[y] for x, y in EQUIPS)
    equip_max = sum(df[y] for _, y in EQUIPS)
    df['score_equip'] = np.where(equip_max > 0, equip_earned / equip_max, 1.0)

    df['score_occ'] = np.where(
        df['seuil'] > 0,
        np.minimum(df['estimated_occupancy_l365d'] / df['seuil'], 1.0),
        0.5
    )

    df['score_rating'] = (df['review_scores_rating'].fillna(2.5) - 1.0) / 4.0

    df['score_nights'] = 1.0 - np.minimum(
        np.abs(df['minimum_nights_x'] - df['minimum_nights_y'].fillna(2.0)) / 5.0, 1.0
    )

    df['score_scalbnb'] = (
        df['score_equip'] * 30
        + df['score_occ'] * 30
        + df['score_rating'] * 25
        + df['score_nights'] * 15
    )
    return df


def compute_score_single(row):
    equip_earned = sum(row[x] * row[y] for x, y in EQUIPS)
    equip_max = sum(row[y] for _, y in EQUIPS)
    score_equip = equip_earned / equip_max if equip_max > 0 else 1.0

    score_occ = min(row['estimated_occupancy_l365d'] / row['seuil'], 1.0) if row['seuil'] > 0 else 0.5

    rating = row['review_scores_rating']
    if pd.isna(rating):
        rating = 2.5
    score_rating = (rating - 1.0) / 4.0

    nights_y = row['minimum_nights_y'] if pd.notna(row.get('minimum_nights_y')) else 2.0
    score_nights = 1.0 - min(abs(row['minimum_nights_x'] - nights_y) / 5.0, 1.0)

    return score_equip * 30 + score_occ * 30 + score_rating * 25 + score_nights * 15


BADGES = [
    (85, "Diamant", "🏆", "#B9F2FF", None),
    (70, "Or", "🥇", "#FFD700", "Diamant"),
    (50, "Argent", "🥈", "#C0C0C0", "Or"),
    (0,  "Bronze", "🥉", "#CD7F32", "Argent"),
]

TIER_RANGES = {
    "Diamant": (85, 100),
    "Or": (70, 85),
    "Argent": (50, 70),
    "Bronze": (0, 50),
}


def get_badge(score):
    for seuil, nom, emoji, couleur, prochain in BADGES:
        if score >= seuil:
            return nom, emoji, couleur, prochain
    return "Bronze", "🥉", "#CD7F32", "Argent"


def get_neighborhood_ranking(df, listing_id, quartier):
    voisins = df[df['neighbourhood_cleansed'] == quartier].copy()
    voisins = voisins.sort_values('score_scalbnb', ascending=False).reset_index(drop=True)
    total = len(voisins)
    idx = voisins[voisins['id'] == listing_id].index
    rang = int(idx[0]) + 1 if len(idx) > 0 else total
    top5 = voisins.head(5)[['id', 'score_scalbnb', 'room_type', 'accommodates']].copy()
    top5.columns = ['ID', 'Score', 'Type', 'Capacité']
    top5.insert(0, 'Rang', range(1, len(top5) + 1))
    top5['Score'] = top5['Score'].round(1)
    top5['ID'] = top5['ID'].apply(lambda x: f"...{str(x)[-4:]}")
    return rang, total, top5


# =============================================================
# CHARGEMENT DES DONNÉES + CALCUL DES SCORES
# =============================================================

df_master = load_data()
df_master = compute_all_scores(df_master)
df_reviews = load_reviews_analysis()

# =============================================================
# EN-TÊTE DE L'APPLICATION
# =============================================================

st.title("🏠 ScalBnB Smart Insights")
st.subheader("Le moteur d'IA pour booster le remplissage de votre Airbnb")
st.write("---")

st.sidebar.header("Tableau de Bord")
st.sidebar.write("Utilisez cet outil pour auditer une annonce à Bordeaux.")

# =============================================================
# SAISIE DE L'IDENTIFIANT
# =============================================================

id_saisi = st.number_input(
    "Entrez l'identifiant (ID) du logement à analyser :",
    min_value=0, step=1, value=0
)

# =============================================================
# LOGIQUE PRINCIPALE
# =============================================================

if id_saisi != 0:
    if id_saisi in df_master['id'].values:

        logement = df_master[df_master['id'] == id_saisi].iloc[0]
        quartier = logement['neighbourhood_cleansed']
        groupe = logement['classement']
        reco = logement['recommandation_finale']

        score = logement['score_scalbnb']
        badge_nom, badge_emoji, badge_couleur, badge_prochain = get_badge(score)
        rang, total_quartier, top5 = get_neighborhood_ranking(df_master, id_saisi, quartier)

        # ---------------------------------------------------------
        # SCORE CARD (toujours visible)
        # ---------------------------------------------------------
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

        # ---------------------------------------------------------
        # ONGLETS
        # ---------------------------------------------------------
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Diagnostic", "🎯 Simulateur", "🏅 Classement", "📧 Email Rapport"
        ])

        # ===================== ONGLET 1 : DIAGNOSTIC =====================
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
                if (pd.isna(reco) or reco.strip() == ""
                        or "correspond déjà" in str(reco)
                        or "possède déjà les standards" in str(reco)):
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
                        if 'estimated_occupancy_l365d' in logement:
                            valeur_occ = logement['estimated_occupancy_l365d']
                            occ_actuel = round(valeur_occ * 100, 1) if valeur_occ <= 1.0 else round(valeur_occ, 1)
                        else:
                            occ_actuel = 15.2
                        st.metric("📈 Votre Taux d'Occupation", f"{occ_actuel} %", delta="-35% vs les Tops")

                    with col2:
                        nb_voisins = int(logement['taille_groupe']) if 'taille_groupe' in logement else 12
                        st.metric("👥 Logements comparés", value=nb_voisins)

                    st.write("---")
                    st.write("### 📋 Votre Plan d'Action Personnalisé :")
                    liste_phrases = str(reco).split("\n")
                    for phrase in liste_phrases:
                        if (phrase.strip() != ""
                                and "correspond déjà" not in phrase
                                and "possède déjà les standards" not in phrase):
                            st.markdown(f"**💡 {phrase.strip()}**")

            # Décomposition du score
            st.write("---")
            st.write("### 📐 Décomposition du Score ScalBnB")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Équipements", f"{logement['score_equip'] * 30:.0f} / 30")
            c2.metric("Occupation", f"{logement['score_occ'] * 30:.0f} / 30")
            c3.metric("Avis Clients", f"{logement['score_rating'] * 25:.0f} / 25")
            c4.metric("Min. Nuits", f"{logement['score_nights'] * 15:.0f} / 15")

            # Analyse des retours voyageurs
            st.write("---")
            st.write("### 💬 Analyse des Retours Voyageurs")

            if id_saisi in df_reviews.index:
                review_row = df_reviews.loc[id_saisi]
                nb_rev = int(review_row['nb_reviews'])
                st.caption(f"Basé sur l'analyse de **{nb_rev} avis** de voyageurs.")

                alertes = []
                for theme, config in REVIEW_THEMES.items():
                    pct = review_row[f'pct_{theme}']
                    if pct >= SEUIL_ALERTE_REVIEWS:
                        alertes.append((config['emoji'], config['label'], pct, int(review_row[f'neg_{theme}'])))

                if alertes:
                    st.warning(
                        f"⚠️ **{len(alertes)} point(s) d'attention** détecté(s) "
                        f"dans les commentaires de vos voyageurs :"
                    )
                    for emoji, label, pct, count in sorted(alertes, key=lambda x: -x[2]):
                        st.markdown(
                            f"**{emoji} {label}** — mentionné dans "
                            f"**{pct:.0f}%** des avis ({count}/{nb_rev})"
                        )
                else:
                    st.success(
                        "✅ Aucun problème récurrent détecté dans les avis de "
                        "vos voyageurs. Continuez ainsi !"
                    )
            else:
                st.info(
                    "📭 Aucun avis voyageur disponible pour ce logement. "
                    "Les recommandations ci-dessus sont basées sur les "
                    "équipements et la configuration de votre annonce."
                )

        # ===================== ONGLET 2 : SIMULATEUR =====================
        with tab2:
            if groupe == -1:
                st.warning(
                    "⚠️ Pas assez de logements comparables dans votre secteur "
                    "pour proposer des simulations fiables."
                )
            else:
                st.write("### 🎯 Simulateur d'Améliorations")
                st.caption(
                    "Cochez les actions que vous comptez réaliser pour voir "
                    "l'impact sur votre score en temps réel."
                )

                RECO_MAP = [
                    ('recor_wifi',  'Wifi_x',             "Ajouter le Wifi"),
                    ('reco_kitchen','kitchen_x',          "Ajouter une cuisine équipée"),
                    ('reco_washer', 'has_washer_x',       "Installer un lave-linge"),
                    ('reco_ac',     'air conditioning_x', "Installer la climatisation"),
                    ('reco_parking','parking_gratuit_x',  "Proposer un parking gratuit"),
                    ('reco_nuit',   'minimum_nights_x',   "Réduire le minimum de nuits"),
                ]

                simulated = logement.copy()
                has_any_reco = False
                actions_cochees = 0

                for reco_col, x_col, label in RECO_MAP:
                    if pd.notna(logement.get(reco_col)):
                        has_any_reco = True

                        # Calculer le gain potentiel
                        test_row = logement.copy()
                        if reco_col == 'reco_nuit':
                            test_row['minimum_nights_x'] = test_row['minimum_nights_y']
                        else:
                            test_row[x_col] = 1
                        gain = compute_score_single(test_row) - score

                        checked = st.checkbox(
                            f"{label}  *(+{gain:.1f} pts)*",
                            key=f"sim_{reco_col}_{id_saisi}"
                        )

                        if checked:
                            actions_cochees += 1
                            if reco_col == 'reco_nuit':
                                simulated['minimum_nights_x'] = simulated['minimum_nights_y']
                            else:
                                simulated[x_col] = 1

                if not has_any_reco:
                    st.success(
                        "✨ Votre logement possède déjà tous les équipements "
                        "recommandés pour votre secteur. Bravo !"
                    )
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
                        st.metric(
                            "Score Simulé",
                            f"{new_score:.0f} / 100",
                            delta=f"+{delta:.0f} pts" if delta > 0 else None,
                        )
                        st.markdown(f"Niveau : {new_badge_emoji} **{new_badge_nom}**")

                    if new_badge_nom != badge_nom and delta > 0:
                        st.success(
                            f"🎉 En appliquant ces {actions_cochees} action(s), "
                            f"vous passeriez au niveau **{new_badge_nom}** !"
                        )

        # ===================== ONGLET 3 : CLASSEMENT =====================
        with tab3:
            st.write(f"### 🏅 Classement dans **{quartier}**")

            percentile = max(round(rang / total_quartier * 100), 1)
            st.metric(
                label=f"Votre position parmi {total_quartier} logements",
                value=f"{rang}e sur {total_quartier}",
                delta=f"Top {percentile}%",
            )

            if groupe == -1:
                st.caption(
                    "⚠️ Attention : ce secteur contient peu de logements comparables, "
                    "le classement est indicatif."
                )

            with st.expander("📋 Voir le Top 5 du quartier"):
                st.dataframe(top5, hide_index=True, use_container_width=True)

            # Jauge visuelle de position
            st.write("#### Votre position sur l'échelle du quartier")
            position_norm = 1 - (rang / total_quartier)
            st.progress(min(max(position_norm, 0.0), 1.0))
            if percentile <= 25:
                st.success("Vous faites partie des meilleurs de votre quartier !")
            elif percentile <= 50:
                st.info("Vous êtes dans la moitié supérieure. Continuez vos efforts !")
            else:
                st.warning("Il y a une marge de progression significative dans votre quartier.")

        # ===================== ONGLET 4 : EMAIL RAPPORT =====================
        with tab4:
            st.write("### 📧 Aperçu du Rapport Mensuel ScalBnB")
            st.caption("Voici à quoi ressemblerait l'email que vous recevriez chaque mois.")

            # Déterminer l'action prioritaire
            reco_priorites = [
                ('recor_wifi',  "Ajouter le Wifi"),
                ('reco_kitchen',"Ajouter une cuisine équipée"),
                ('reco_washer', "Installer un lave-linge"),
                ('reco_parking',"Proposer un parking gratuit"),
                ('reco_ac',     "Installer la climatisation"),
                ('reco_nuit',   "Réduire votre nombre de nuits minimum"),
            ]
            top_action = None
            for col, txt in reco_priorites:
                if pd.notna(logement.get(col)):
                    top_action = txt
                    break

            mois = datetime.now().strftime("%B %Y").capitalize()

            action_html = ""
            if top_action:
                action_html = f"""
                <div style="background:#fff3cd; padding:12px; border-radius:8px; margin:12px 0;">
                    <p style="margin:0;"><b>🎯 Action prioritaire ce mois-ci :</b></p>
                    <p style="margin:4px 0 0 0;">{top_action}</p>
                </div>"""

            reviews_html = ""
            if id_saisi in df_reviews.index:
                rev_row = df_reviews.loc[id_saisi]
                email_alertes = []
                for theme, config in REVIEW_THEMES.items():
                    pct = rev_row[f'pct_{theme}']
                    if pct >= SEUIL_ALERTE_REVIEWS:
                        email_alertes.append((config['emoji'], config['label'], pct))
                if email_alertes:
                    items = "".join(
                        f"<li>{em} {lab} ({pct:.0f}% des avis)</li>"
                        for em, lab, pct in sorted(email_alertes, key=lambda x: -x[2])
                    )
                    reviews_html = f"""
                <div style="background:#f8d7da; padding:12px; border-radius:8px; margin:12px 0;">
                    <p style="margin:0 0 6px 0;"><b>💬 Retours voyageurs à traiter :</b></p>
                    <ul style="margin:0; padding-left:20px;">{items}</ul>
                </div>"""

            badge_section = ""
            if badge_prochain:
                pts = TIER_RANGES[badge_prochain][0] - score
                badge_section = f"""
                <div style="background:#d4edda; padding:12px; border-radius:8px; margin:12px 0;">
                    <p style="margin:0;">🚀 <b>Objectif du mois</b> : Plus que <b>{pts:.0f} points</b>
                    pour atteindre le niveau <b>{badge_prochain}</b> !</p>
                </div>"""

            email_html = f"""
            <div style="border:2px solid #e0e0e0; border-radius:12px; padding:0;
                        max-width:500px; margin:auto; font-family:Arial,sans-serif;
                        overflow:hidden;">
                <div style="text-align:center;
                            background:linear-gradient(135deg, #667eea, #764ba2);
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

                    {badge_section}
                    {action_html}
                    {reviews_html}

                    <div style="text-align:center; margin-top:20px;">
                        <a href="#" style="background:linear-gradient(135deg,#667eea,#764ba2);
                           color:white; padding:12px 24px; border-radius:8px;
                           text-decoration:none; font-weight:bold;">
                           Voir mon tableau de bord complet
                        </a>
                    </div>

                    <div style="text-align:center; color:#aaa; font-size:11px;
                                margin-top:24px; padding-top:16px;
                                border-top:1px solid #eee;">
                        <p>Cet email est envoyé maximum 2 fois par mois.</p>
                        <p><a href="#" style="color:#aaa;">Se désinscrire</a> |
                           <a href="#" style="color:#aaa;">Gérer mes préférences</a></p>
                    </div>
                </div>
            </div>
            """
            st.markdown(email_html, unsafe_allow_html=True)

            st.write("")
            with st.expander("📖 Stratégie anti-fatigue : pourquoi seulement 2 emails/mois ?"):
                st.markdown("""
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
                """)

    else:
        st.error(
            "❌ Cet identifiant de logement n'existe pas dans la base de données "
            "de Bordeaux. Veuillez vérifier votre saisie."
        )
else:
    st.info(
        "👋 Bienvenue sur l'application de démo ScalBnB ! "
        "Veuillez saisir un identifiant de logement ci-dessus "
        "pour lancer l'audit automatique de l'IA."
    )

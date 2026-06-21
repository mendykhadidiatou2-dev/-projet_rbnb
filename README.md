# ScalBnB Smart Insights

**Moteur d'audit intelligent pour optimiser les annonces Airbnb sur Bordeaux Metropole.**

ScalBnB analyse les performances de **10 947 logements** Airbnb et fournit a chaque hote un diagnostic personnalise avec un score, des recommandations concretes et un systeme de gamification pour encourager le passage a l'action.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.58-red?logo=streamlit)
![Pandas](https://img.shields.io/badge/Pandas-3.0-purple?logo=pandas)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Apercu de l'application

L'utilisateur saisit l'identifiant de son logement et obtient instantanement :

| Onglet | Fonctionnalite |
|--------|---------------|
| **Diagnostic** | Classification du logement (Champion / Standard / Flop), plan d'action personnalise, analyse des retours voyageurs par NLP |
| **Simulateur** | Checklist interactive : cocher une amelioration recalcule le score en temps reel |
| **Classement** | Position du logement dans le leaderboard de son quartier |
| **Email Rapport** | Maquette d'email mensuel gamifie + strategie anti-fatigue (max 2 emails/mois) |

---

## Fonctionnalites techniques

### Score ScalBnB (0-100)

Chaque logement recoit un score composite base sur 4 axes :

| Composante | Poids | Source |
|-----------|-------|--------|
| Equipements | 30 pts | Wifi, cuisine, lave-linge, climatisation, parking vs profil des leaders du secteur |
| Taux d'occupation | 30 pts | Jours reserves sur 365 jours vs seuil du segment |
| Avis clients | 25 pts | Note moyenne des voyageurs (1-5) |
| Flexibilite (min. nuits) | 15 pts | Ecart avec la strategie des leaders |

### Systeme de badges

| Badge | Score | Description |
|-------|-------|-------------|
| Bronze | 0-49 | Logement avec des lacunes significatives |
| Argent | 50-69 | Marge de progression identifiee |
| Or | 70-84 | Bon logement, pas encore elite |
| Diamant | 85-100 | Top performer du secteur |

### Analyse NLP des retours voyageurs

L'application analyse **469 309 commentaires** de voyageurs pour detecter 5 categories de problemes recurrents : proprete, bruit, confort de la literie, temperature, et qualite de l'accueil. Un seuil d'alerte se declenche lorsqu'un theme depasse 10% des avis.

### Strategie anti-fatigue email

Pour maximiser l'engagement sans irriter l'utilisateur :
- **Email 1** (1er du mois) : rapport mensuel avec score, badge et action prioritaire
- **Email 2** (15 du mois) : envoye uniquement si le score est a moins de 5 points du niveau superieur
- **Pause automatique** : apres 3 mois au niveau Diamant, passage a 1 email par trimestre

---

## Structure du projet

```
projet_rbnb/
├── app.py                     # Application Streamlit principale
├── requirements.txt           # Dependances Python
├── data/
│   ├── master_final.csv       # Dataset enrichi (10 947 logements)
│   ├── reviews_analysis.csv   # Analyse NLP pre-calculee des avis
│   ├── neighbourhoods.csv     # Quartiers de Bordeaux Metropole
│   └── neighbourhoods.geojson # Contours geographiques
├── notebooks/
│   └── pipeline.ipynb         # Pipeline complet : nettoyage, feature engineering, classification, recommandations
```

---

## Installation et lancement

### 1. Cloner le projet

```bash
git clone https://github.com/VOTRE_USERNAME/projet_rbnb.git
cd projet_rbnb
```

### 2. Creer l'environnement virtuel

```bash
python -m venv env
# Windows
env\Scripts\activate
# Mac/Linux
source env/bin/activate
```

### 3. Installer les dependances

```bash
pip install -r requirements.txt
```

### 4. Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvre automatiquement dans le navigateur a l'adresse `http://localhost:8501`.

---

## Donnees

Les donnees traitees (`data/`) sont incluses dans le repository. Les donnees brutes proviennent de [Inside Airbnb](http://insideairbnb.com/get-the-data/) (Bordeaux, France) et ne sont pas incluses en raison de leur taille (>300 Mo). Les notebooks dans `notebooks/` documentent l'ensemble du pipeline de traitement.

### Pipeline de traitement (`notebooks/pipeline.ipynb`)

Le notebook reproduit l'integralite du traitement des donnees brutes :

1. **Chargement** : `listings.csv`, `calendar.csv`, `reviews.csv` depuis Inside Airbnb
2. **Nettoyage** : prix (suppression `$` et `,`), filtrage des locations courte duree (≤30 nuits)
3. **Feature engineering** : extraction de 5 equipements cles (Wifi, cuisine, lave-linge, climatisation, parking gratuit) depuis le champ JSON `amenities`
4. **Calcul d'occupation** : taux de reservation sur 365 jours via le calendrier de disponibilite
5. **Segmentation** : terciles de prix par quartier + type de logement
6. **Classification** : seuil au 75e percentile d'occupation dans chaque segment (Top vs Standard)
7. **Recommandations dynamiques** : comparaison equipements du listing vs profil des leaders du segment
8. **Export** : generation de `master_final.csv` (10 947 lignes, 33 colonnes)

---

## Exemples d'identifiants pour tester

| ID | Profil | Interet |
|----|--------|---------|
| `813125` | Flop avec equipements manquants | Recommandations equipements + score bas |
| `45922084` | Flop avec problemes de proprete | Alertes retours voyageurs (57% avis negatifs) |
| `457462` | Standard | Recommandation min. nuits |
| `656926` | Standard avec bonnes reviews | Score moyen, peu d'alertes |

---

## Technologies utilisees

- **Python 3.10+** — langage principal
- **Streamlit** — framework d'application web interactive
- **Pandas / NumPy** — manipulation et analyse de donnees
- **NLP par mots-cles** — analyse thematique bilingue (FR/EN) des commentaires voyageurs

---

## Auteur

Projet realise dans le cadre d'une soutenance academique.

---

## Licence

Ce projet est distribue sous licence MIT. Voir le fichier `LICENSE` pour plus de details.

# ScalBnB - Audit intelligent d'annonces Airbnb

Projet de data science realisé dans le cadre d'une soutenance academique.

L'idee de depart : on a recupere les donnees open data de **10 947 annonces Airbnb sur Bordeaux Metropole** (source : [Inside Airbnb](http://insideairbnb.com/get-the-data/)), et on s'est demandé comment aider concretement un hote a comprendre pourquoi son logement se loue moins bien que ses voisins — et surtout quoi faire pour ameliorer ca.

Le resultat, c'est une application Streamlit qui permet de taper l'identifiant d'un logement et d'obtenir un diagnostic complet : ou il se situe par rapport a la concurrence, ce qui lui manque, et ce qu'il gagnerait a changer.

## Ce que fait l'application

Quand on entre un ID de logement, l'app affiche 4 onglets :

- **Diagnostic** — Le logement est classé Champion, Standard ou Flop selon son taux d'occupation par rapport aux autres logements du meme quartier/type/gamme de prix. On voit tout de suite les equipements manquants et les actions a mener. On a aussi integré une analyse des commentaires voyageurs (469 000+ avis) pour detecter les problemes recurrents (proprete, bruit, literie, etc.).

- **Simulateur** — C'est la partie gamification : chaque recommandation est une case a cocher. Quand on coche "Ajouter le Wifi" ou "Reduire le minimum de nuits", le score se recalcule en direct et on voit tout de suite combien de points on gagne et si on change de niveau.

- **Classement** — Le logement est positionné dans un classement par quartier. On peut voir le Top 5 et savoir si on est dans les 25% meilleurs ou les 50% derniers.

- **Email Rapport** — Une maquette de ce a quoi ressemblerait un email mensuel envoye a l'hote. L'idee c'est de limiter a 2 emails par mois max pour ne pas spammer, avec un contenu qui change a chaque fois (score, badge, action du mois).

## Le score ScalBnB

On a construit un score sur 100 qui prend en compte 4 choses :

- **Equipements (30 pts)** — Est-ce que le logement a les memes equipements que les meilleurs de son secteur (Wifi, cuisine, lave-linge, clim, parking) ?
- **Occupation (30 pts)** — Combien de jours il est reserve sur un an, compare au seuil du segment ?
- **Avis clients (25 pts)** — La note moyenne laissee par les voyageurs.
- **Nuits minimum (15 pts)** — Est-ce que le logement impose trop de nuits minimum par rapport aux leaders ?

Selon le score, le logement obtient un badge : Bronze (0-49), Argent (50-69), Or (70-84) ou Diamant (85-100).

## Comment lancer le projet

```bash
# Cloner le repo
git clone https://github.com/mendykhadidiatou2-dev/-projet_rbnb.git
cd -projet_rbnb

# Creer un environnement virtuel et installer les dependances
python -m venv env
env\Scripts\activate        # Windows
pip install -r requirements.txt

# Lancer l'app
streamlit run app.py
```

Ca ouvre automatiquement le navigateur sur `http://localhost:8501`.

## Structure du projet

```
app.py                  -> L'application Streamlit (tout le code est la-dedans)
requirements.txt        -> Les librairies a installer (streamlit, pandas, numpy)
data/
  master_final.csv      -> Le dataset final avec les 10 947 logements et leurs scores
  reviews_analysis.csv  -> L'analyse pre-calculee des commentaires voyageurs
  neighbourhoods.csv    -> Liste des quartiers
  neighbourhoods.geojson -> Contours geographiques des quartiers
notebooks/
  pipeline.ipynb        -> Le notebook qui genere master_final.csv a partir des donnees brutes
```

## Le pipeline de donnees

Tout le traitement est dans `notebooks/pipeline.ipynb`. En gros :

1. On charge les fichiers bruts d'Inside Airbnb (`listings.csv`, `calendar.csv`, `reviews.csv`)
2. On nettoie les prix, on filtre les locations courte duree (≤30 nuits)
3. On extrait 5 equipements cles depuis le champ `amenities` (qui est un gros JSON par annonce)
4. On calcule le taux d'occupation sur 365 jours grace au calendrier de disponibilite
5. On decoupe les logements en segments (quartier + type + gamme de prix par terciles)
6. Dans chaque segment, on classe les logements : ceux au-dessus du 75e percentile d'occupation sont "Tops", les autres "Standard"
7. On compare les equipements de chaque Standard avec le profil moyen des Tops pour generer des recommandations
8. On exporte le tout dans `master_final.csv`

Les fichiers bruts ne sont pas dans le repo (trop volumineux, >300 Mo) mais sont telechargeables gratuitement sur [Inside Airbnb](http://insideairbnb.com/get-the-data/).

## Pour tester

Quelques IDs a essayer dans l'app :

- **813125** — Un logement Flop avec des equipements manquants (cuisine, nuits minimum). Score bas, recommandations visibles.
- **45922084** — Un Flop avec des problemes de proprete detectes dans les avis (57% de mentions negatives).
- **457462** — Un Standard avec juste une recommandation sur les nuits minimum.

## Technologies

- Python 3.10+
- Streamlit
- Pandas / NumPy
- Analyse de texte par mots-cles (FR/EN) sur les commentaires voyageurs

## Auteur

Khadidiatou Mendy — Projet academique, 2026.

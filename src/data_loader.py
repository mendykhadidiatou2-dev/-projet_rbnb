"""Chargement des jeux de données pré-calculés consommés par l'application.

Ces fichiers sont produits par notebooks/pipeline.ipynb à partir des données
brutes Inside Airbnb (trop volumineuses pour être versionnées ici).
"""

import pandas as pd
import streamlit as st


@st.cache_data
def load_data(path: str = "data/master_final.csv") -> pd.DataFrame:
    """Charge le dataset des logements avec leurs scores et recommandations."""
    return pd.read_csv(path)


@st.cache_data
def load_reviews_analysis(path: str = "data/reviews_analysis.csv") -> pd.DataFrame:
    """Charge l'analyse pré-calculée des avis voyageurs, indexée par listing_id."""
    return pd.read_csv(path, index_col="listing_id")
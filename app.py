# ==========================================================
# H-DATA – AI Data Doctor
# Développé par HAMDINOU Moulaye Driss © 2025
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
import os

# ==========================================================
# CONFIGURATION
# ==========================================================
st.set_page_config(page_title="H-DATA – AI Data Doctor", page_icon="🧠", layout="wide")

st.markdown("""
<style>
h1, h2, h3, h4 {color:#00C853;}
.reportview-container {
    background-color: #0d1117;
    color: #e0e0e0;
}
.sidebar .sidebar-content {
    background-color: #111827;
}
</style>
""", unsafe_allow_html=True)

if os.path.exists("hdata_logo.png"):
    st.image("hdata_logo.png", width=180)

st.title("🧠 H-DATA – AI Data Doctor")
st.markdown("_Analyse. Corrige. Visualise._")
st.markdown("**Développé par HAMDINOU Moulaye Driss © 2025**")

# ==========================================================
# UPLOAD DES DONNÉES
# ==========================================================
st.header("📂 Importation des données")

uploaded_file = st.file_uploader("Importez un fichier CSV ou Excel :", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.success(f"✅ Fichier chargé avec succès : {uploaded_file.name}")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {e}")
        st.stop()

    # ==========================================================
    # DIAGNOSTIC IA AUTOMATIQUE
    # ==========================================================
    st.header("🤖 Diagnostic intelligent des données")

    def analyse_data(df):
        diag = []
        for col in df.columns:
            if df[col].isnull().sum() > 0:
                diag.append((col, "Valeurs manquantes", df[col].isnull().sum(), "Remplacer par moyenne/médiane"))
            if df[col].dtype in [np.float64, np.int64]:
                outliers = ((df[col] - df[col].mean()).abs() > 3 * df[col].std()).sum()
                if outliers > 0:
                    diag.append((col, "Valeurs aberrantes", outliers, "Remplacer par médiane"))
            if df[col].duplicated().any():
                diag.append((col, "Doublons", df[col].duplicated().sum(), "Supprimer doublons"))
        return pd.DataFrame(diag, columns=["Colonne", "Problème", "Nb Occurrences", "Proposition IA"])

    diag_df = analyse_data(df)
    st.dataframe(diag_df)

    # ==========================================================
    # CORRECTION AUTOMATIQUE
    # ==========================================================
    st.header("🧹 Application des corrections IA")

    if st.checkbox("✅ Appliquer automatiquement les corrections suggérées"):
        for _, row in diag_df.iterrows():
            col = row["Colonne"]
            if "manquantes" in row["Problème"]:
                if df[col].dtype in [np.float64, np.int64]:
                    df[col].fillna(df[col].median(), inplace=True)
            if "aberrantes" in row["Problème"]:
                mean, std = df[col].mean(), df[col].std()
                df[col] = np.where((df[col] - mean).abs() > 3*std, df[col].median(), df[col])
            if "Doublons" in row["Problème"]:
                df.drop_duplicates(subset=[col], inplace=True)
        st.success("✅ Corrections appliquées automatiquement avec succès.")
        st.dataframe(df.head())

    # ==========================================================
    # VISUALISATIONS RAPIDES
    # ==========================================================
    st.header("📊 Visualisations rapides")

    col_choice = st.selectbox("Choisir une colonne numérique :", df.select_dtypes(include=np.number).columns)
    if col_choice:
        fig, ax = plt.subplots(figsize=(6, 3))
        sns.histplot(df[col_choice], bins=30, kde=True, ax=ax, color="#0078D7")
        ax.set_title(f"Distribution de {col_choice}")
        st.pyplot(fig)

        corr = df.select_dtypes(include=np.number).corr()
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        sns.heatmap(corr, cmap="Blues", ax=ax2)
        ax2.set_title("Heatmap de corrélation")
        st.pyplot(fig2)

    # ==========================================================
    # EXPORT CSV
    # ==========================================================
    st.header("💾 Export des données nettoyées")
    os.makedirs("outputs", exist_ok=True)
    cleaned_path = f"outputs/data_cleaned_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(cleaned_path, index=False)
    st.success(f"✅ Données sauvegardées : {cleaned_path}")

    # ==========================================================
    # GÉNÉRATION DU RAPPORT PDF
    # ==========================================================
    st.header("📄 Génération du rapport PDF")

    sections = st.multiselect(
        "Choisissez les sections à inclure dans le rapport :",
        ["Résumé général", "Diagnostic IA", "Propositions de correction", "Graphiques"],
        default=["Résumé général", "Diagnostic IA"]
    )

    if st.button("📄 Générer le rapport PDF"):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        if os.path.exists("hdata_logo.png"):
            story.append(Image("hdata_logo.png", width=160, height=60))
        story.append(Spacer(1, 20))
        story.append(Paragraph("<b>H-DATA – Rapport d’analyse des données</b>", styles["Title"]))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"Fichier : {uploaded_file.name}", styles["Normal"]))
        story.append(Paragraph(f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
        story.append(Paragraph("Analyste : HAMDINOU Moulaye Driss", styles["Normal"]))
        story.append(Spacer(1, 20))

        if "Résumé général" in sections:
            story.append(Paragraph("<b>Résumé général :</b>", styles["Heading2"]))
            story.append(Paragraph(f"Nombre de lignes : {len(df)}", styles["Normal"]))
            story.append(Paragraph(f"Nombre de colonnes : {len(df.columns)}", styles["Normal"]))
            story.append(Spacer(1, 10))

        if "Diagnostic IA" in sections:
            story.append(Paragraph("<b>Diagnostic IA :</b>", styles["Heading2"]))
            table_data = [diag_df.columns.tolist()] + diag_df.values.tolist()
            table = Table(table_data)
            table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0078D7")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white)
            ]))
            story.append(table)
            story.append(Spacer(1, 10))

        story.append(Spacer(1, 20))
        story.append(Paragraph("<b>H-DATA © 2025 – Développé par HAMDINOU Moulaye Driss</b>", styles["Italic"]))
        doc.build(story)
        buffer.seek(0)

        pdf_bytes = buffer.getvalue()
        st.download_button(
            label="📥 Télécharger le rapport PDF",
            data=pdf_bytes,
            file_name="rapport_hdata.pdf",
            mime="application/pdf"
        )
        st.success("✅ Rapport PDF généré avec succès.")

    # ==========================================================
    # LIEN VERS GRAFANA
    # ==========================================================
    st.markdown("---")
    st.subheader("🌐 Visualisation externe")
    st.markdown("[Ouvrir les données dans Grafana](http://localhost:3000/)", unsafe_allow_html=True)

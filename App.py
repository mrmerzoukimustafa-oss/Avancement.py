import streamlit as st
import pandas as pd
from datetime import date
import re

st.set_page_config(page_title="Avancements - Règles métier", layout="wide")
st.title("📈 Gestion des avancements avec règles")

# ---- Initialisation ----
if 'propositions' not in st.session_state:
    st.session_state.propositions = []

# ---- Upload fichier ----
st.sidebar.header("1. Charger le fichier")
uploaded_file = st.sidebar.file_uploader("Choisissez 'avancement dp taourirt.xlsx'", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, sheet_name='Feuil1', header=None)
        st.sidebar.success("Fichier chargé !")
    except Exception as e:
        st.error(f"Erreur : {e}")
        st.stop()
else:
    st.info("Veuillez charger le fichier Excel dans la barre latérale.")
    st.stop()

# ---- Extraction des données ----
noms_employes = df.iloc[0, 1:].dropna().tolist()
noms_employes = [str(nom).strip().title() for nom in noms_employes]

annees = []
for idx in range(1, len(df)):
    val = df.iloc[idx, 0]
    if pd.notna(val):
        try:
            annees.append(int(val))
        except:
            pass
annees = sorted(set(annees))

if not noms_employes or not annees:
    st.error("Format du fichier invalide.")
    st.stop()

# ---- Fonction pour extraire le type (niveau/catégorie) et le grade ----
def parse_avancement(cell):
    """Retourne (type, valeur) avec type = 'niveau' ou 'categorie'"""
    cell = str(cell).strip().lower()
    if 'niveau' in cell:
        return ('niveau', cell)
    elif 'catégorie' in cell or 'categorie' in cell:
        return ('categorie', cell)
    return (None, cell)

# ---- Récupérer l'historique complet d'un employé ----
def get_history(employe_nom):
    # Trouver colonne
    col_idx = None
    for i, nom in enumerate(df.iloc[0, 1:].values):
        if str(nom).strip().lower() == employe_nom.lower():
            col_idx = i + 1
            break
    if col_idx is None:
        return []
    history = []
    for idx in range(1, len(df)):
        annee = df.iloc[idx, 0]
        if pd.isna(annee):
            continue
        try:
            annee = int(annee)
        except:
            continue
        valeur = df.iloc[idx, col_idx]
        if pd.notna(valeur):
            typ, lib = parse_avancement(valeur)
            if typ:
                history.append((annee, typ, lib))
    # Trier par année
    history.sort(key=lambda x: x[0])
    return history

# ---- Règles métier : calcul du prochain avancement ----
def next_promotion(history):
    """
    history : liste de (année, type, libellé)
    Retourne (année_prévue, type_attendu, explication)
    """
    if not history:
        # Premier avancement : on suppose qu'on commence par un niveau ?
        # Par défaut, on retourne "aucun historique"
        return None, None, "Aucun historique"

    # Dernier avancement
    last_year, last_type, last_lib = history[-1]
    current_year = date.today().year

    # Règle 1 : après 1 an d'obtention d'un niveau, proposer catégorie
    if last_type == 'niveau':
        next_year = last_year + 1
        if next_year >= current_year:
            return next_year, 'categorie', f"Dernier niveau en {last_year} → catégorie attendue en {next_year}"
        else:
            return None, None, f"Catégorie attendue en {next_year} (dépassé)"

    # Dernier avancement est une catégorie
    if last_type == 'categorie':
        # Chercher la date de la dernière catégorie (la plus récente)
        # Mais il peut y avoir plusieurs catégories ? On prend la dernière
        # Règle : la troisième année après la catégorie, mérite un niveau
        # => année + 2 (car +1 ?) "la troisième année après" : ex catégorie en 2020, troisième année = 2023 ? 
        # Interprétation: année de la catégorie = N, la 3ème année après = N+3 ? Non, "la troisième année après" signifie N+3 (2020->2023)
        # Mais souvent on dit "après 2 ans" pour un niveau. Vérifions: "aprés 1 ans de obtention d'un niveau l'agent proposé au catégorie" => Niveau en N, catégorie en N+1.
        # "la troisième anné apres la catégorie ,l'agent doit mirite un niveau" => Catégorie en M, niveau en M+3.
        # "si l'agent ne prend pas la catégorie ,une année aprés prend un niveau" => Si pas de catégorie, niveau en M+1.
        # Donc pour une catégorie obtenue, le prochain niveau est à M+3.
        next_year = last_year + 3
        if next_year >= current_year:
            return next_year, 'niveau', f"Dernière catégorie en {last_year} → niveau attendu en {next_year}"
        else:
            # Vérifier si une catégorie a été manquée ? On peut aussi proposer un niveau si dépassé.
            # Mais on va retourner quand même.
            return None, None, f"Niveau attendu en {next_year} (dépassé)"

    return None, None, "Règle non définie"

# ---- Interface : deux onglets principaux ----
tab1, tab2, tab3 = st.tabs(["📅 Par année", "🔮 Prochain avancement", "✏️ Propositions"])

# ---- Onglet 1 : Avancements par année (inchangé) ----
with tab1:
    st.header("Avancements par année")
    annee_selec = st.selectbox("Année", annees)
    if annee_selec:
        ligne_idx = None
        for idx in range(1, len(df)):
            val = df.iloc[idx, 0]
            if pd.notna(val) and int(val) == annee_selec:
                ligne_idx = idx
                break
        if ligne_idx:
            data = []
            for col_idx, nom in enumerate(noms_employes):
                cellule = df.iloc[ligne_idx, col_idx+1]
                if pd.notna(cellule):
                    typ, _ = parse_avancement(cellule)
                    data.append({"Employé": nom, "Avancement": cellule, "Type": typ.capitalize() if typ else "?"})
            if data:
                st.dataframe(pd.DataFrame(data), use_container_width=True)
            else:
                st.info("Aucun avancement cette année.")
        else:
            st.warning("Année non trouvée")

# ---- Onglet 2 : Prochain avancement selon règles ----
with tab2:
    st.header("Prochain avancement prévu (règles métier)")
    employe_choisi = st.selectbox("Choisir un employé", noms_employes, key="prochain")
    history = get_history(employe_choisi)
    if history:
        st.write("**Historique des avancements :**")
        hist_df = pd.DataFrame(history, columns=["Année", "Type", "Libellé"])
        st.dataframe(hist_df, use_container_width=True)
        
        next_year, next_type, expl = next_promotion(history)
        if next_year and next_type:
            st.success(f"📌 **Prochain avancement attendu : {next_type.capitalize()} en {next_year}**")
            st.caption(expl)
            # Bouton pour proposer automatiquement cet avancement
            if st.button("➕ Proposer cet avancement"):
                # Vérifier si déjà proposé
                already = any(p["Employé"] == employe_choisi and p["Année"] == next_year for p in st.session_state.propositions)
                if not already:
                    st.session_state.propositions.append({
                        "Employé": employe_choisi,
                        "Année": next_year,
                        "Nouvelle catégorie": f"{next_type} attendu",
                        "Statut": "proposé",
                        "Date": date.today().strftime("%d/%m/%Y"),
                        "Notes": f"Proposé automatiquement selon règle : {expl}"
                    })
                    st.success("Proposition ajoutée !")
                    st.rerun()
                else:
                    st.warning("Proposition déjà existante.")
        else:
            st.info(f"Aucun avancement futur prévu. {expl}")
    else:
        st.info("Aucun historique pour cet employé.")

# ---- Onglet 3 : Gestion des propositions (inchangé) ----
with tab3:
    st.header("Propositions d'avancement")
    if st.session_state.propositions:
        df_prop = pd.DataFrame(st.session_state.propositions)
        st.dataframe(df_prop, use_container_width=True)
        
        # Permettre de modifier le statut d'une proposition
        st.subheader("Modifier le statut")
        prop_index = st.selectbox("Sélectionner une proposition", range(len(st.session_state.propositions)),
                                   format_func=lambda i: f"{st.session_state.propositions[i]['Employé']} - {st.session_state.propositions[i]['Année']} ({st.session_state.propositions[i]['Statut']})")
        nouveau_statut = st.selectbox("Nouveau statut", ["proposé", "approuvé", "refusé"],
                                      index=["proposé","approuvé","refusé"].index(st.session_state.propositions[prop_index]["Statut"]))
        if st.button("Mettre à jour"):
            st.session_state.propositions[prop_index]["Statut"] = nouveau_statut
            st.success("Statut mis à jour")
            st.rerun()
        
        # Exporter
        csv = df_prop.to_csv(index=False)
        st.download_button("📥 Exporter les propositions (CSV)", csv, "propositions.csv", "text/csv")
    else:
        st.info("Aucune proposition pour le moment.")

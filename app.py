import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Avancements", layout="wide")
st.title("📈 Gestion des avancements")

# ---- Initialisation de la session ----
if 'propositions' not in st.session_state:
    st.session_state.propositions = []

# ---- Upload du fichier Excel ----
st.sidebar.header("1. Charger le fichier")
uploaded_file = st.sidebar.file_uploader("Choisissez le fichier 'avancement dp taourirt.xlsx'", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, sheet_name='Feuil1', header=None)
        st.sidebar.success("Fichier chargé !")
    except Exception as e:
        st.error(f"Erreur de lecture : {e}")
        st.stop()
else:
    st.info("Veuillez charger le fichier Excel dans la barre latérale.")
    st.stop()

# ---- Extraction des employés et des années ----
# La première ligne contient les noms des employés (colonne B et suivantes)
noms_employes = df.iloc[0, 1:].dropna().tolist()
noms_employes = [str(nom).strip().title() for nom in noms_employes]

# La première colonne contient les années (lignes 1 à ...)
annees = []
for idx in range(1, len(df)):
    val = df.iloc[idx, 0]
    if pd.notna(val):
        try:
            annees.append(int(val))
        except:
            pass
annees = sorted(set(annees))

if not noms_employes:
    st.error("Aucun employé trouvé. Vérifiez que la première ligne contient les noms.")
    st.stop()
if not annees:
    st.error("Aucune année trouvée. Vérifiez que la première colonne contient les années.")
    st.stop()

# ---- Fonction pour récupérer le type (niveau ou catégorie) ----
def get_type(cell):
    cell = str(cell).lower()
    if 'niveau' in cell:
        return "Niveau"
    elif 'catégorie' in cell:
        return "Catégorie"
    return "Inconnu"

# ---- Interface principale : deux onglets ----
tab1, tab2 = st.tabs(["📅 Avancements par année", "✏️ Proposer un avancement"])

# ---- Onglet 1 : Avancements par année ----
with tab1:
    st.header("Consulter les avancements par année")
    annee_selectionnee = st.selectbox("Choisissez une année", annees)
    
    if annee_selectionnee:
        # Trouver la ligne correspondant à cette année
        ligne_idx = None
        for idx in range(1, len(df)):
            val = df.iloc[idx, 0]
            if pd.notna(val) and int(val) == annee_selectionnee:
                ligne_idx = idx
                break
        if ligne_idx is None:
            st.warning(f"Aucune donnée pour l'année {annee_selectionnee}")
        else:
            # Construire le tableau
            data = []
            for col_idx, nom in enumerate(noms_employes):
                cellule = df.iloc[ligne_idx, col_idx+1]  # +1 car la première colonne est l'année
                if pd.notna(cellule):
                    valeur = str(cellule).strip()
                    typ = get_type(valeur)
                    data.append({
                        "Employé": nom,
                        "Avancement": valeur,
                        "Type": typ
                    })
            if data:
                st.subheader(f"Avancements en {annee_selectionnee}")
                df_result = pd.DataFrame(data)
                st.dataframe(df_result, use_container_width=True)
            else:
                st.info(f"Aucun avancement enregistré pour {annee_selectionnee}.")

# ---- Onglet 2 : Proposer un avancement ----
with tab2:
    st.header("Proposer un avancement")
    selected_employe = st.selectbox("Employé", noms_employes, key="emp_select")
    
    with st.form("proposition_form"):
        annee = st.number_input("Année", value=date.today().year, step=1)
        nouvelle_categorie = st.text_input("Nouvelle catégorie (ex: niveau 8/16)")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Proposer")
        if submitted:
            if not nouvelle_categorie:
                st.error("Veuillez saisir une catégorie.")
            else:
                st.session_state.propositions.append({
                    "Employé": selected_employe,
                    "Année": annee,
                    "Nouvelle catégorie": nouvelle_categorie,
                    "Statut": "proposé",
                    "Date": date.today().strftime("%d/%m/%Y"),
                    "Notes": notes
                })
                st.success("Proposition ajoutée !")
                st.rerun()
    
    # Afficher les propositions existantes
    if st.session_state.propositions:
        st.subheader("Propositions en cours")
        props_df = pd.DataFrame(st.session_state.propositions)
        st.dataframe(props_df, use_container_width=True)
        
        # Bouton pour exporter
        csv = props_df.to_csv(index=False)
        st.download_button("📥 Télécharger toutes les propositions (CSV)", csv, "propositions.csv", "text/csv")

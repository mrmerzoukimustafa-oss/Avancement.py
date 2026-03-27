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

# ---- Extraction des employés ----
# La première ligne contient les noms des employés (colonne B et suivantes)
noms_employes = df.iloc[0, 1:].dropna().tolist()
# Nettoyer : enlever espaces, mettre en titre
noms_employes = [str(nom).strip().title() for nom in noms_employes]

if not noms_employes:
    st.error("Aucun employé trouvé. Vérifiez que la première ligne contient les noms.")
    st.stop()

# ---- Fonction pour récupérer l'historique d'un employé ----
def get_history(employe_nom):
    # Trouver la colonne correspondant à l'employé
    colonne_index = None
    for i, nom in enumerate(df.iloc[0, 1:].values):
        if str(nom).strip().lower() == employe_nom.lower():
            colonne_index = i + 1  # +1 car la colonne 0 est l'année
            break
    if colonne_index is None:
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
        valeur = df.iloc[idx, colonne_index]
        if pd.notna(valeur):
            history.append((annee, str(valeur).strip()))
    return history

# ---- Sélection de l'employé ----
st.sidebar.header("2. Choisir un employé")
selected_employe = st.sidebar.selectbox("Employé", noms_employes)

# ---- Affichage de l'historique ----
st.header(f"Historique – {selected_employe}")
history = get_history(selected_employe)
if history:
    hist_df = pd.DataFrame(history, columns=["Année", "Catégorie obtenue"])
    st.dataframe(hist_df, use_container_width=True)
else:
    st.info("Aucun avancement enregistré pour cet employé.")

# ---- Proposition d'un nouvel avancement ----
st.header("Proposer un avancement")
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

# ---- Affichage des propositions pour l'employé sélectionné ----
st.header("Propositions en cours")
props_emp = [p for p in st.session_state.propositions if p["Employé"] == selected_employe]
if props_emp:
    for idx, prop in enumerate(props_emp):
        with st.expander(f"{prop['Année']} – {prop['Nouvelle catégorie']} ({prop['Statut']})"):
            st.write(f"**Date :** {prop['Date']}")
            st.write(f"**Notes :** {prop['Notes']}")
            # Boutons pour changer le statut
            col1, col2, col3 = st.columns(3)
            with col1:
                if prop["Statut"] != "approuvé":
                    if st.button("Approuver", key=f"app_{idx}"):
                        prop["Statut"] = "approuvé"
                        st.success("Statut mis à jour")
                        st.rerun()
            with col2:
                if prop["Statut"] != "refusé":
                    if st.button("Refuser", key=f"ref_{idx}"):
                        prop["Statut"] = "refusé"
                        st.success("Statut mis à jour")
                        st.rerun()
            with col3:
                if st.button("🗑️ Supprimer", key=f"del_{idx}"):
                    st.session_state.propositions.remove(prop)
                    st.success("Proposition supprimée")
                    st.rerun()
else:
    st.info("Aucune proposition pour cet employé.")

# ---- Option pour exporter les propositions (facultatif) ----
if st.session_state.propositions:
    st.sidebar.header("3. Exporter")
    export_df = pd.DataFrame(st.session_state.propositions)
    csv = export_df.to_csv(index=False)
    st.sidebar.download_button("📥 Télécharger les propositions (CSV)", csv, "propositions.csv", "text/csv")

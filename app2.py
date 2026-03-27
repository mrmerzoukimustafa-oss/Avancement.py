import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Avancements", layout="wide")
st.title("📈 Gestion des avancements")

# ---- Chargement du fichier historique ----
@st.cache_data
def load_avancements():
    try:
        df = pd.read_excel('avancement dp taourirt.xlsx', sheet_name='Feuil1', header=None)
        return df
    except FileNotFoundError:
        st.error("Fichier 'avancement dp taourirt.xlsx' introuvable. Placez-le dans le même dossier.")
        return None
    except Exception as e:
        st.error(f"Erreur de lecture : {e}")
        return None

# ---- Fonctions de gestion des promotions proposées ----
def load_propositions():
    try:
        return pd.read_csv('propositions.csv')
    except FileNotFoundError:
        # Créer un fichier vide avec les colonnes
        empty_df = pd.DataFrame(columns=['Employé', 'Année', 'Nouvelle catégorie', 'Statut', 'Date proposition', 'Notes'])
        empty_df.to_csv('propositions.csv', index=False)
        return empty_df

def save_proposition(employe, annee, nouvelle_categorie, notes):
    df = load_propositions()
    nouvelle_ligne = pd.DataFrame([{
        'Employé': employe,
        'Année': annee,
        'Nouvelle catégorie': nouvelle_categorie,
        'Statut': 'proposé',
        'Date proposition': date.today().strftime('%Y-%m-%d'),
        'Notes': notes
    }])
    df = pd.concat([df, nouvelle_ligne], ignore_index=True)
    df.to_csv('propositions.csv', index=False)

def update_proposition_status(index, nouveau_statut):
    df = load_propositions()
    df.loc[index, 'Statut'] = nouveau_statut
    df.to_csv('propositions.csv', index=False)

# ---- Extraction des employés depuis l'historique ----
def extract_employees(df):
    """Récupère la liste des employés à partir de la première ligne du fichier"""
    if df is None:
        return []
    # La première ligne (index 0) contient les noms des employés (colonnes B, C, ...)
    noms = df.iloc[0, 1:].dropna().tolist()
    # Nettoyer les noms
    employes = [str(nom).strip() for nom in noms]
    return employes

# ---- Construction de l'historique par employé ----
def build_history(df, employe_nom):
    """Extrait l'historique des avancements pour un employé donné"""
    if df is None:
        return []
    # Trouver la colonne de l'employé (par nom, ignore la casse)
    cols = df.iloc[0, 1:].tolist()
    for i, col in enumerate(cols):
        if str(col).strip().lower() == employe_nom.lower():
            col_index = i + 1  # +1 car la première colonne est l'année
            break
    else:
        return []

    history = []
    for row_idx in range(1, len(df)):
        annee = df.iloc[row_idx, 0]
        if pd.isna(annee):
            continue
        try:
            annee = int(annee)
        except:
            continue
        valeur = df.iloc[row_idx, col_index]
        if pd.notna(valeur):
            history.append((annee, str(valeur).strip()))
    return history

# ---- Interface Streamlit ----
df_hist = load_avancements()

if df_hist is not None:
    # Extraire la liste des employés
    employes = extract_employees(df_hist)
    if not employes:
        st.warning("Aucun employé trouvé dans le fichier.")
        st.stop()

    st.sidebar.header("Filtres")
    selected_employe = st.sidebar.selectbox("Choisir un employé", employes)

    # Afficher l'historique
    st.header(f"Historique des avancements – {selected_employe}")
    history = build_history(df_hist, selected_employe)
    if history:
        history_df = pd.DataFrame(history, columns=['Année', 'Catégorie obtenue'])
        st.dataframe(history_df, use_container_width=True)
    else:
        st.info("Aucun avancement enregistré pour cet employé.")

    # ---- Gestion des propositions d'avancement ----
    st.header("Proposer un nouvel avancement")
    with st.form("proposition_form"):
        annee_prop = st.number_input("Année", value=date.today().year, step=1)
        nouvelle_cat = st.text_input("Nouvelle catégorie (ex: niveau 8/16)")
        notes = st.text_area("Notes (optionnel)")
        submitted = st.form_submit_button("Proposer")
        if submitted:
            if not nouvelle_cat:
                st.error("Veuillez saisir la nouvelle catégorie.")
            else:
                save_proposition(selected_employe, annee_prop, nouvelle_cat, notes)
                st.success("Proposition enregistrée !")

    # ---- Afficher les propositions existantes ----
    st.header("Propositions en attente / approuvées / refusées")
    df_prop = load_propositions()
    if not df_prop.empty:
        # Filtrer par employé sélectionné
        df_emp_prop = df_prop[df_prop['Employé'] == selected_employe]
        if not df_emp_prop.empty:
            # Ajouter une colonne d'action pour modifier le statut
            for idx, row in df_emp_prop.iterrows():
                with st.expander(f"{row['Année']} – {row['Nouvelle catégorie']} ({row['Statut']})"):
                    st.write(f"**Date :** {row['Date proposition']}")
                    st.write(f"**Notes :** {row['Notes']}")
                    new_status = st.selectbox(
                        "Changer le statut",
                        ['proposé', 'approuvé', 'refusé'],
                        index=['proposé', 'approuvé', 'refusé'].index(row['Statut']),
                        key=f"status_{idx}"
                    )
                    if new_status != row['Statut']:
                        update_proposition_status(idx, new_status)
                        st.success("Statut mis à jour")
                        st.rerun()
        else:
            st.info("Aucune proposition pour cet employé.")
    else:
        st.info("Aucune proposition enregistrée.")
else:
    st.stop()

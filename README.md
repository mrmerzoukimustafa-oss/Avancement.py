# Gestion des avancements

Application Streamlit pour visualiser l’historique des avancements à partir d’un fichier Excel et proposer de nouvelles promotions.

## 🚀 Utilisation

1. Déposez votre fichier `avancement dp taourirt.xlsx` dans le même dossier que l’application.
2. Lancez l’app localement avec `streamlit run app.py` ou déployez sur Streamlit Cloud.
3. Choisissez un employé dans la barre latérale.
4. Visualisez son historique, proposez un avancement, et gérez les propositions.

## 📂 Structure du fichier attendu

Le fichier Excel doit avoir :
- **Première ligne** : les noms des employés (une colonne par employé, à partir de la colonne B)
- **Première colonne** : les années (de 2012 à 2028)
- **Cellules** : catégories au format `niveau X/Y` ou `catégorie X/Y`

## 🔧 Déploiement sur Streamlit Cloud

1. Créez un dépôt GitHub avec ces fichiers.
2. Connectez‑vous sur [share.streamlit.io](https://share.streamlit.io).
3. Cliquez sur **"New app"**, sélectionnez le dépôt, la branche, et le fichier `app.py`.
4. L’application sera en ligne.

## 📝 Notes

- Les propositions sont stockées dans un fichier `propositions.csv` qui sera créé automatiquement.
- Pour des données persistantes, assurez‑vous de ne pas supprimer ce fichier lors des redéploiements (sur Streamlit Cloud, il est perdu après chaque redémarrage ; pour conserver les données, utilisez une base de données externe, mais ce n’est pas nécessaire pour un usage simple).

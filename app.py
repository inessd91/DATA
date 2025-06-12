import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
# 📥 Chargement des fichiers
df_all = pd.read_csv("df_all.csv", parse_dates=['InvoiceDate'])
df_clients = pd.read_csv("df_clients.csv", parse_dates=['InvoiceDate'])
df_original = pd.read_csv("data.csv", encoding='ISO-8859-1')

# Ajout de colonnes
for df in [df_all, df_clients]:
    df['YearMonth'] = df['InvoiceDate'].dt.to_period('M').astype(str)
    df['InvoiceHour'] = df['InvoiceDate'].dt.hour

# Interface
st.title("🛍️ Dashboard E-commerce : Analyse des ventes")

# Sélection du dataset
dataset_choice = st.sidebar.radio("Sélectionner un dataset :", ["df_all", "df_clients"])
df = df_all if dataset_choice == "df_all" else df_clients

# Filtres utilisateurs
min_date, max_date = df['InvoiceDate'].min(), df['InvoiceDate'].max()
selected_dates = st.sidebar.date_input("Période", [min_date, max_date])
pays = sorted(df['Country'].dropna().unique())
selected_country = st.sidebar.selectbox("Pays", ["Tous"] + pays)
if selected_country != "Tous":
    df = df[df['Country'] == selected_country]
if dataset_choice == "df_clients":
    clients = sorted(df['CustomerID'].dropna().astype(int).unique())
    selected_client = st.sidebar.selectbox("Client", ["Tous"] + list(clients))
    if selected_client != "Tous":
        df = df[df['CustomerID'] == int(selected_client)]
df = df[(df['InvoiceDate'] >= pd.to_datetime(selected_dates[0])) & (df['InvoiceDate'] <= pd.to_datetime(selected_dates[1]))]
if dataset_choice == "df_all":
    if not st.sidebar.checkbox("Inclure les retours", value=True):
        df = df[df['IsReturn'] == False]
    if not st.sidebar.checkbox("Inclure les annulations", value=True):
        df = df[df['IsCancelled'] == False]

# 🧭 Onglets principaux
tab1, tab2, tab3, tab4 = st.tabs(["📄 Présentation", "📊 Statistiques", "🏆 Produits & Clients", "📍 Carte & Recos"])

# 1️⃣ Présentation des données
with tab1:
    
    st.header("📄 Présentation du jeu de données")
    st.markdown("### 1. Présentation générale")
    st.markdown("""
    **Source** : [Kaggle - Online Retail Dataset](https://www.kaggle.com/datasets/carrie1/ecommerce-data)  
    **Période couverte** : Décembre 2010 à décembre 2011  
    **Lieu** : Boutique en ligne basée au Royaume-Uni
    """)
    #
    with st.expander("📦 Dimensions du dataset original"):
        col1, col2 = st.columns(2)
        col1.metric("Nombre de lignes", f"{df_original.shape[0]:,}")
        col2.metric("Nombre de colonnes", f"{df_original.shape[1]}")

    with st.expander("📊 Types de variables"):
        st.dataframe(pd.DataFrame(df_original.dtypes, columns=["Type de donnée"]))

    with st.expander("🧼 Données manquantes"):
        st.dataframe(df_original.isnull().sum().to_frame("Valeurs manquantes"))

    #st.subheader("📦 Dimensions du dataset original")
    #st.write(f"Nombre de lignes : {df_original.shape[0]}")
    #st.write(f"Nombre de colonnes : {df_original.shape[1]}")
    #st.dataframe(df_original.head())

    #st.subheader("📊 Types de variables")
    #st.write(pd.DataFrame(df_original.dtypes, columns=["Type de donnée"]))

    #st.subheader("🧼 Données manquantes")
    #st.write(df_original.isnull().sum().to_frame("Valeurs manquantes"))

    #st.subheader("✅ Nettoyage appliqué")
    st.markdown("### 2. Nettoyage appliqué")
    st.markdown("""
    - Suppression des lignes avec `UnitPrice <= 0` ou `Quantity = 0`
    - Suppression des doublons exacts
    - Formatage de `InvoiceDate` en datetime
    - Séparation :
        - `df_all` : toutes les transactions (clients connus ou anonymes)
        - `df_clients` : uniquement les transactions avec identifiant client
    - Création de nouvelles variables : `TotalPrice`, `IsReturn`, `InvoiceHour`, etc.
    """)

    #st.subheader("📁 Datasets générés après nettoyage")
    st.markdown("### 3. Datasets générés après nettoyage")

    with st.expander("Transactions globales – Dataset `df_all`"):
        st.write(f"**Nombre de lignes** : {df_all.shape[0]}")
        st.write(f"**Nombre de colonnes** : {df_all.shape[1]}")
        st.markdown("""
        - Inclut **toutes** les transactions, y compris les clients sans identifiant.
        - Utilisé pour les analyses **globales** (ventes, produits, pays, etc.)
        - Colonnes ajoutées :
            - `TotalPrice` : Montant total par ligne (Quantity × UnitPrice)
            - `IsReturn` : True si la facture commence par "C" (retour)
            - `IsCancelled` : True si quantité ou prix est négatif
            - `YearMonth`, `InvoiceHour` : Dates transformées
        """)
        if st.button("📦 Aperçu df_all"):
            st.dataframe(df_all.head())

    with st.expander("Transactions clients identifiés – Dataset `df_clients`"):
        st.write(f"**Nombre de lignes** : {df_clients.shape[0]}")
        st.write(f"**Nombre de colonnes** : {df_clients.shape[1]}")
        st.markdown("""
        - Sous-ensemble de `df_all` filtré sur les lignes avec `CustomerID` non nul.
        - Utile pour les analyses **clients**, segmentation, fidélité, etc.
        - Même structure que `df_all`, avec uniquement les clients identifiés.
        """)
        if st.button("👥 Aperçu df_clients"):
            st.dataframe(df_clients.head())
    
    #st.subheader("🌀 Nuage de mots : Contexte de l'e-commerce")
    st.markdown("### 4. Nuage de mots : Contexte de l'e-commerce")

    st.markdown("""
    > Ce nuage de mots est basé sur un texte décrivant les enjeux de l’e-commerce :  
    > comportement client, rapidité de service, stratégies de vente...
    """)

    st.image("wordcloud_ecommerce.png", use_container_width=True)


# 2️⃣ Statistiques
with tab2:
    st.header("📈 Indicateurs clés")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Ventes totales", f"{df['TotalPrice'].sum():,.0f} £")
    col2.metric("🧾 Commandes", df['InvoiceNo'].nunique())
    col3.metric("📦 Articles vendus", int(df['Quantity'].sum()))
    col4.metric("🌍 Pays couverts", df['Country'].nunique())
    # --- KPIs Fidélisation ---
    if dataset_choice == "df_clients" and 'CustomerID' in df.columns:
        commandes_par_client = df.groupby('CustomerID')['InvoiceNo'].nunique()
        clients_fideles = commandes_par_client[commandes_par_client > 1].count()
        total_clients = commandes_par_client.count()
        taux_retour_client = (clients_fideles / total_clients) * 100 if total_clients > 0 else 0
        nombre_moyen_commandes = commandes_par_client.mean() if total_clients > 0 else 0
        valeur_vie_client = df.groupby('CustomerID')['TotalPrice'].sum().mean() if total_clients > 0 else 0

        st.subheader("🔁 KPIs Fidélisation")
        st.write(f"Taux de retour client : {taux_retour_client:.2f} %")
        st.write(f"Nombre moyen de commandes par client : {nombre_moyen_commandes:.2f}")
        st.write(f"Valeur vie client moyenne : {valeur_vie_client:.2f} £")


    # Statistiques descriptives sur TotalPrice et Quantity
    mean_ventes = df['TotalPrice'].mean()
    median_ventes = df['TotalPrice'].median()
    std_ventes = df['TotalPrice'].std()

    mean_quantite = df['Quantity'].mean()
    median_quantite = df['Quantity'].median()
    std_quantite = df['Quantity'].std()
    st.subheader("📅 Tendance linéaire des ventes mensuelles")
    monthly_sales = df.groupby('YearMonth')['TotalPrice'].sum().reset_index()
    monthly_sales['YearMonth_num'] = np.arange(len(monthly_sales))  # variable numérique pour la régression

    plt.figure(figsize=(10,5))
    sns.regplot(x='YearMonth_num', y='TotalPrice', data=monthly_sales, marker='o', color='blue')
    plt.xticks(ticks=monthly_sales['YearMonth_num'], labels=monthly_sales['YearMonth'], rotation=45)
    plt.title("Tendance linéaire des ventes mensuelles")
    plt.xlabel("Mois")
    plt.ylabel("Ventes totales (£)")
    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.clf()

    st.subheader("📊 Statistiques descriptives")
    st.write(f"Ventes (TotalPrice) : moyenne = {mean_ventes:.2f} £, médiane = {median_ventes:.2f} £, écart-type = {std_ventes:.2f}")
    st.write(f"Quantités vendues : moyenne = {mean_quantite:.2f}, médiane = {median_quantite:.2f}, écart-type = {std_quantite:.2f}")

    st.subheader("📅 Ventes mensuelles")
    monthly_sales = df.groupby('YearMonth')['TotalPrice'].sum().reset_index()
    fig_month = px.line(monthly_sales, x='YearMonth', y='TotalPrice', title="Ventes par mois")
    st.plotly_chart(fig_month)

    st.subheader("🕒 Heures de commandes")
    plt.figure(figsize=(10,4))
    sns.histplot(df['InvoiceHour'], bins=24, kde=False, color='darkorange')
    plt.title("Répartition horaire des commandes")
    plt.xlabel("Heure")
    plt.ylabel("Nombre")
    st.pyplot(plt.gcf())
    plt.clf()

# 3️⃣ Produits & Clients
with tab3:
    st.header("📦 Top 10 Produits")
    top_products = (df.groupby(['StockCode', 'Description'])
                    .agg({'Quantity': 'sum', 'TotalPrice': 'sum'})
                    .reset_index()
                    .sort_values('Quantity', ascending=False)
                    .head(10))
    fig1, ax1 = plt.subplots(figsize=(10,6))
    sns.barplot(data=top_products, y='Description', x='Quantity', palette="Blues_d", ax=ax1)
    ax1.set_title("Top Produits (Quantité)")
    st.pyplot(fig1)
    st.download_button("📥 Télécharger Top Produits", top_products.to_csv(index=False), "top_produits.csv")

    if dataset_choice == "df_clients":
        st.header("👥 Top 10 Clients")
        top_clients = df.groupby('CustomerID')['TotalPrice'].sum().reset_index().sort_values('TotalPrice', ascending=False).head(10)
        fig2 = px.bar(top_clients, x='CustomerID', y='TotalPrice', title="Top Clients")
        st.plotly_chart(fig2)
        st.download_button("📥 Télécharger Top Clients", top_clients.to_csv(index=False), "top_clients.csv")

# 4️⃣ Carte & Recommandations
with tab4:
    st.header("🌍 Carte géographique des ventes")
    country_sales = df.groupby('Country')['TotalPrice'].sum().reset_index()
    fig_map = px.choropleth(country_sales, locations="Country", locationmode="country names",
                            color="TotalPrice", title="Ventes par pays",
                            color_continuous_scale="Viridis")
    st.plotly_chart(fig_map)

    st.subheader("✅ Recommandations")
    st.markdown("""
    - 🕒 Optimiser les campagnes sur les horaires de forte activité
    - 🔁 Identifier les produits à fort taux de retour pour enquête
    - 💡 Fidéliser les meilleurs clients avec des offres ciblées
    - 🌍 Cibler les pays à fort potentiel de croissance
    """)

# 📤 Export global
st.sidebar.subheader("📥 Exporter données filtrées")
st.sidebar.download_button("💾 CSV", df.to_csv(index=False), "donnees_filtrees.csv")
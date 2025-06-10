import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

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
    st.markdown("""
    **Source** : [Kaggle - Online Retail Dataset](https://www.kaggle.com/datasets/carrie1/ecommerce-data)  
    **Période couverte** : Décembre 2010 à décembre 2011  
    **Lieu** : Boutique en ligne basée au Royaume-Uni
    """)
    
    st.subheader("📦 Dimensions du dataset original")
    st.write(f"Nombre de lignes : {df_original.shape[0]}")
    st.write(f"Nombre de colonnes : {df_original.shape[1]}")
    st.dataframe(df_original.head())

    st.subheader("📊 Types de variables")
    st.write(pd.DataFrame(df_original.dtypes, columns=["Type de donnée"]))

    st.subheader("🧼 Données manquantes")
    st.write(df_original.isnull().sum().to_frame("Valeurs manquantes"))

    st.subheader("✅ Nettoyage appliqué")
    st.markdown("""
    - Suppression des lignes avec `UnitPrice <= 0` ou `Quantity = 0`
    - Suppression des doublons exacts
    - Formatage de `InvoiceDate` en datetime
    - Séparation :
        - `df_all` : toutes les transactions (clients connus ou anonymes)
        - `df_clients` : uniquement les transactions avec identifiant client
    - Création de nouvelles variables : `TotalPrice`, `IsReturn`, `InvoiceHour`, etc.
    """)

# 2️⃣ Statistiques
with tab2:
    st.header("📈 Indicateurs clés")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Ventes totales", f"{df['TotalPrice'].sum():,.0f} £")
    col2.metric("🧾 Commandes", df['InvoiceNo'].nunique())
    col3.metric("📦 Articles vendus", int(df['Quantity'].sum()))
    col4.metric("🌍 Pays couverts", df['Country'].nunique())

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

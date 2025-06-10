import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px 

# Config page
st.set_page_config(page_title="Analyse E-commerce", layout="wide")

# Chargement des datasets (avec cache)
@st.cache_data
def load_original():
    df = pd.read_csv("data.csv", encoding="ISO-8859-1")
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    return df

@st.cache_data
def load_df_all():
    df_all = pd.read_csv("df_all.csv")
    df_all['InvoiceDate'] = pd.to_datetime(df_all['InvoiceDate'])
    return df_all

@st.cache_data
def load_df_clients():
    df_clients = pd.read_csv("df_clients.csv")

    return df_clients

# Chargement effectif
df_original = load_original()
df_all = load_df_all()
df_clients = load_df_clients()

# Navigation via sidebar
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Choisissez une section :", ["Présentation", "Statistiques", "Visualisations"])

# ========================
# Page Présentation
# ========================
if page == "Présentation":
    st.title("🛍️ Présentation du jeu de données et du nettoyage")

    st.markdown("""
    ### 🗂️ 1. Source du jeu de données

    Ce jeu de données provient de [Kaggle](https://www.kaggle.com/datasets/carrie1/ecommerce-data).  
    Il contient les transactions d'un site e-commerce basé au Royaume-Uni entre **décembre 2010 et décembre 2011**.
    """)

    st.markdown("### 📦 2. Dataset original (`data.csv`)")
    st.write(f"- Nombre d'observations : {df_original.shape[0]}")
    st.write(f"- Nombre de variables : {df_original.shape[1]}")
    st.dataframe(df_original.head())

    st.markdown("""
    ### 🧹 3. Nettoyage réalisé

    Afin de préparer les données pour l’analyse, plusieurs étapes de nettoyage ont été réalisées dans le notebook :

    - 🔸 **Suppression des lignes avec des valeurs incohérentes**, telles que :
        - Quantité négative (`Quantity < 0`) non liée à une facture de retour
        - Prix unitaire nul ou négatif (`UnitPrice <= 0`)
    - 🔸 **Suppression des doublons** exacts dans les transactions
    - 🔸 **Conversion des types de données** :
        - `InvoiceDate` en format datetime
        - autres colonnes au format approprié
    - 🔸 **Gestion des lignes sans identifiant client (`CustomerID`)** :
        - Ces lignes sont conservées dans `df_all` pour les analyses globales de ventes
        - Elles sont exclues de `df_clients` afin de permettre des analyses par client (ex. : RFM, fidélité)

    Deux jeux de données sont ainsi générés :
        - **`df_all`** : contient toutes les transactions valides (avec ou sans identifiant client)
        - **`df_clients`** : contient uniquement les lignes avec un identifiant client valide
    """)
    
    #Creation des variables 
    st.markdown("""
    ### 🧪 4. Création de nouvelles variables pertinentes

    Des variables supplémentaires ont été créées à partir des données brutes, afin de faciliter les analyses statistiques, comportementales et commerciales.

    - **`TotalPrice`** : Montant total d’une ligne (`Quantity × UnitPrice`)
    - **`IsReturn`** : Indique si la ligne correspond à un retour produit (`Quantity < 0`)
    - **`IsCancelled`** : Facture annulée (numéro de facture commençant par "C")
    - **`InvoiceHour`** : Heure de la commande (extraite de `InvoiceDate`)
    - **`InvoiceTotalItems`** : Nombre total d’articles dans une facture
    - **`CustomerTotalSpent`** : Montant total dépensé par un client
    - **`CustomerNumOrders`** : Nombre total de commandes passées par client

    Ces variables permettent :
    - De mieux comprendre les comportements d’achat
    - De mesurer la performance commerciale
    - D’identifier les clients à fort potentiel ou à risque
    - De détecter les anomalies (commandes annulées, pics horaires, retours fréquents)

    """)


    # Section df_all
    st.markdown("### 📊 5. Dataset `df_all` (transactions nettoyées)")
    st.write(f"- Nombre d'observations : {df_all.shape[0]}")
    st.write(f"- Nombre de variables : {df_all.shape[1]}")
    st.write("#### Valeurs manquantes dans `df_all`")
    missing_all = df_all.isnull().sum()
    if missing_all.sum() == 0:
        st.success("✅ Aucune valeur manquante.")
    else:
        st.write(missing_all[missing_all > 0])
    st.dataframe(df_all.head())

    # Section df_clients
    st.markdown("### 👥 6. Dataset `df_clients` (transactions avec client identifié)")
    st.write(f"- Nombre d'observations : {df_clients.shape[0]}")
    st.write(f"- Nombre de variables : {df_clients.shape[1]}")
    st.write("#### Valeurs manquantes dans `df_clients`")
    missing_clients = df_clients.isnull().sum()
    if missing_clients.sum() == 0:
        st.success("✅ Aucune valeur manquante.")
    else:
        st.write(missing_clients[missing_clients > 0])
    st.dataframe(df_clients.head())


###------------------------
# page stat
###------------------------
if page == "Statistiques":
    st.title("📊 Statistiques descriptives")

    # --- FILTRES ---
    st.sidebar.header("Filtres")

    # Plages de dates (sur df_all)
    date_min = df_all['InvoiceDate'].min()
    date_max = df_all['InvoiceDate'].max()

    date_range = st.sidebar.date_input(
        "Période d'analyse",
        [date_min, date_max],
        min_value=date_min,
        max_value=date_max
    )

    # Filtre pays
    countries = ["Tous les pays"] + sorted(df_all['Country'].dropna().unique().tolist())
    selected_country = st.sidebar.selectbox("Pays", countries)

    # --- FILTRAGE DES DONNÉES ---

    # Filtrer df_all
    df_all_filtered = df_all.copy()
    if len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        df_all_filtered = df_all_filtered[(df_all_filtered['InvoiceDate'] >= start_date) & (df_all_filtered['InvoiceDate'] <= end_date)]

    if selected_country != "Tous les pays":
        df_all_filtered = df_all_filtered[df_all_filtered['Country'] == selected_country]

    # Filtrer df_clients (pas de date ici, car pas de InvoiceDate dans df_clients)
    df_clients_filtered = df_clients.copy()
    if selected_country != "Tous les pays":
        df_clients_filtered = df_clients_filtered[df_clients_filtered['Country'] == selected_country]

    # Calcul moyenne panier pour clients filtrés
    df_clients_filtered = df_clients_filtered[df_clients_filtered['CustomerNumOrders'] > 0].copy()
    df_clients_filtered['CustomerAvgBasket'] = df_clients_filtered['CustomerTotalSpent'] / df_clients_filtered['CustomerNumOrders']

    # --- AFFICHAGE DES STATISTIQUES ---

    st.markdown("### 1. Statistiques générales")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Nombre de lignes", f"{df_all_filtered.shape[0]:,}")
    col2.metric("Nombre de factures", f"{df_all_filtered['InvoiceNo'].nunique()}")
    col3.metric("Nombre de produits", f"{df_all_filtered['Description'].nunique()}")
    col4.metric("Chiffre d'affaires total", f"{df_all_filtered['TotalPrice'].sum():,.2f} £")

    st.markdown("#### Évolution du chiffre d'affaires par jour")
    df_all_filtered['InvoiceDateOnly'] = df_all_filtered['InvoiceDate'].dt.date
    ca_journalier = df_all_filtered.groupby('InvoiceDateOnly')['TotalPrice'].sum().reset_index()

    fig = px.line(ca_journalier, x='InvoiceDateOnly', y='TotalPrice',
                  title="Chiffre d'affaires quotidien", markers=True)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Statistiques descriptives des variables numériques")
    st.dataframe(df_all_filtered.describe())

    st.markdown("---")

    st.markdown("### 2. Statistiques clients")

    st.write(f"Nombre de clients : {df_clients_filtered['CustomerID'].nunique()}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Dépense moyenne par client", f"{df_clients_filtered['CustomerTotalSpent'].mean():.2f} £")
    col2.metric("Panier moyen par commande", f"{df_clients_filtered['CustomerAvgBasket'].mean():.2f} £")
    col3.metric("Commandes moyennes par client", f"{df_clients_filtered['CustomerNumOrders'].mean():.1f}")

    st.markdown("#### Top 5 clients les plus dépensiers")
    top_clients = df_clients_filtered.sort_values(by='CustomerTotalSpent', ascending=False).head(5)
    st.table(top_clients[['CustomerID', 'CustomerTotalSpent', 'CustomerNumOrders']])

    st.markdown("#### Distribution du total dépensé par client")
    st.bar_chart(df_clients_filtered.set_index('CustomerID')['CustomerTotalSpent'].sort_values(ascending=False))

##--------------------------------
#page visualiasation
###------------------------------
elif page == "Visualisations":
    st.title("📊 Visualisations interactives")

    # ------------------------------
    # Filtres (sidebar)
    # ------------------------------
    st.sidebar.header("🔍 Filtres interactifs")

    # 1. Heure
    hour_range = st.sidebar.slider("⏰ Plage horaire :", 0, 23, (0, 23))

    # 2. Pays (dropdown pour top produits)
    countries = sorted(df_all['Country'].dropna().unique())
    selected_country = st.sidebar.selectbox("🌍 Pays (Top produits)", countries)

    # 3. Multi-pays (checkbox pour carte/pie)
    selected_countries = st.sidebar.multiselect("🌐 Pays à afficher (ventes par pays)", countries, default=countries)

    # 4. Période (pour évolution CA)
    date_min = df_all['InvoiceDate'].min().date()
    date_max = df_all['InvoiceDate'].max().date()
    date_range = st.sidebar.date_input("📅 Période :", [date_min, date_max], min_value=date_min, max_value=date_max)

    # 5. Slider commandes par client
    client_order_range = st.sidebar.slider("📦 Nb commandes par client :", 1, 100, (1, 20))

    # ------------------------------
    # Préparation des données
    # ------------------------------
    df_viz = df_all.copy()
    df_viz['InvoiceHour'] = df_viz['InvoiceDate'].dt.hour
    df_viz['Date'] = df_viz['InvoiceDate'].dt.date

    if len(date_range) == 2:
        df_viz = df_viz[(df_viz['InvoiceDate'] >= pd.to_datetime(date_range[0])) &
                        (df_viz['InvoiceDate'] <= pd.to_datetime(date_range[1]))]

    # ------------------------------
    # 1️⃣ Ventes par heure (bar chart)
    # ------------------------------
    st.subheader("1️⃣ Ventes par heure de la journée")
    df_hour = df_viz[(df_viz['InvoiceHour'] >= hour_range[0]) & (df_viz['InvoiceHour'] <= hour_range[1])]
    hour_dist = df_hour.groupby('InvoiceHour').size().reset_index(name='NbCommandes')
    fig1 = px.bar(hour_dist, x='InvoiceHour', y='NbCommandes', title="Nombre de commandes par heure")
    st.plotly_chart(fig1, use_container_width=True)

    # ------------------------------
    # 2️⃣ Top 10 produits les plus vendus (bar chart)
    # ------------------------------
    st.subheader("2️⃣ Top 10 des produits les plus vendus par pays")
    df_country = df_viz[df_viz['Country'] == selected_country]
    top_products = df_country.groupby('Description')['Quantity'].sum().sort_values(ascending=False).head(10).reset_index()
    fig2 = px.bar(top_products, x='Quantity', y='Description', orientation='h',
                  title=f"Top 10 produits – {selected_country}")
    fig2.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig2, use_container_width=True)

    # ------------------------------
    # 3️⃣ Répartition des ventes par pays (pie chart)
    # ------------------------------
    st.subheader("3️⃣ Répartition des ventes par pays")
    df_pays = df_viz[df_viz['Country'].isin(selected_countries)]
    sales_by_country = df_pays.groupby('Country')['TotalPrice'].sum().reset_index()
    fig3 = px.pie(sales_by_country, names='Country', values='TotalPrice',
                  title="Répartition du chiffre d'affaires par pays")
    st.plotly_chart(fig3, use_container_width=True)

    # ------------------------------
    # 4️⃣ Évolution du CA dans le temps (line chart)
    # ------------------------------
    st.subheader("4️⃣ Évolution du chiffre d'affaires dans le temps")
    df_daily = df_viz.groupby('Date')['TotalPrice'].sum().reset_index()
    fig4 = px.line(df_daily, x='Date', y='TotalPrice', title="Chiffre d'affaires quotidien", markers=True)
    st.plotly_chart(fig4, use_container_width=True)

    # ------------------------------
    # 5️⃣ Distribution des commandes par client (histogramme)
    # ------------------------------
    st.subheader("5️⃣ Distribution du nombre de commandes par client")
    df_clients_filtered = df_clients.copy()
    df_clients_filtered = df_clients_filtered[df_clients_filtered['CustomerNumOrders'].between(client_order_range[0], client_order_range[1])]
    fig5 = px.histogram(df_clients_filtered, x="CustomerNumOrders", nbins=20,
                        title="Nombre de commandes par client")
    st.plotly_chart(fig5, use_container_width=True)

    # ------------------------------
    # Aperçu des données brutes filtrées
    # ------------------------------
    st.markdown("### 📦 Aperçu des transactions filtrées")
    st.dataframe(df_viz[['InvoiceDate', 'InvoiceNo', 'CustomerID', 'Description', 'Quantity', 'TotalPrice']].head(20))

## Dashboard E-commerce – Analyse des ventes
Ce projet propose une application interactive construite avec Streamlit permettant d’analyser un dataset e-commerce complet à partir des transactions d'une boutique en ligne britannique.
Elle permet d'explorer les performances commerciales, le comportement client, les produits les plus vendus et les zones géographiques de vente.

 ### Fonctionnalités principales :
   - Statistiques globales sur les ventes, articles vendus, clients, pays
   - Analyse temporelle (mensuelle, horaire)
   - Indicateurs de fidélisation client
   - Top produits et clients
   - Carte des ventes par pays
   - Recommandations stratégiques pour le développement commercial

### Datasets utilisés:
| Fichier          | Description                                                      |
| ---------------- | ---------------------------------------------------------------- |
| `data.csv`       | Dataset brut original provenant de Kaggle                        |
| `df_all.csv`     | Dataset nettoyé contenant toutes les transactions                |
| `df_clients.csv` | Sous-ensemble de `df_all` avec uniquement les clients identifiés |


### Prétraitement appliqué:
- Suppression des doublons et lignes incohérentes (Quantity = 0, UnitPrice <= 0)

- Ajout de colonnes dérivées :
  - TotalPrice = Quantity × UnitPrice
  - IsReturn, IsCancelled pour la gestion des retours et annulations
  - InvoiceHour, YearMonth pour l’analyse temporelle

- Séparation des datasets selon la présence ou non d’un identifiant client (CustomerID)

### Aperçu de l'application:
  - Présentation générale des datasets (dimensions, types de variables, données manquantes)
  - Indicateurs clés : ventes totales, commandes, pays, quantités
  - Visualisations interactives : tendances mensuelles, heures de commande, cartes de chaleur
  - Top produits et Top clients
  - Carte des ventes mondiale
  - Recommandations basées sur les données

### Source des données:
Ce projet s’appuie sur le jeu de données Online Retail Dataset publié sur Kaggle: https://www.kaggle.com/datasets/carrie1/ecommerce-data 
Il contient environ 500 000 lignes de transactions entre décembre 2010 et décembre 2011.

### Recommandations business clés:
Les ventes sont fortement concentrées au Royaume-Uni

Heures de commande optimales : entre 9h et 14h

Le Top 10 produits génère une part significative du volume

Besoin d’actions ciblées sur les clients fidèles

Opportunités à développer dans certains pays émergents

### Fichiers utiles:
app.py – Code principal de l’application

df_all.csv, df_clients.csv, data.csv – Datasets (prétraités ou bruts)

wordcloud_ecommerce.png – Image utilisée pour illustrer le contexte e-commerce

requirements.txt – Dépendances Python

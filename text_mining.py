import requests
from bs4 import BeautifulSoup
import nltk
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Télécharger le texte de l'article
url = "https://www.lemonde.fr/economie/article/2024/11/21/internet-et-la-seconde-main-sapent-le-marche-francais-de-l-habillement_6407206_3234.html"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
texte = soup.get_text()

# Nettoyage du texte
texte = texte.lower()
texte = texte.translate(str.maketrans('', '', string.punctuation))

# Tokenisation
nltk.download('punkt')
tokens = word_tokenize(texte)

# Suppression des stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('french'))
tokens_filtrés = [mot for mot in tokens if mot not in stop_words]

# Texte nettoyé
texte_nettoye = " ".join(tokens_filtrés)
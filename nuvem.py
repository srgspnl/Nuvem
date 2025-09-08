import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import spacy
import spacy.cli
import re

# Garantir que o modelo está instalado
spacy.cli.download("pt_core_news_sm")

# Carregar modelo spaCy
nlp = spacy.load("pt_core_news_sm")

# Título da aplicação
st.title("Nuvem de Palavras com spaCy")

# Entrada de texto
text = st.text_area("Cole seu texto abaixo (máximo 500 palavras):", height=200)

if text:
    words = text.split()
    if len(words) > 500:
        st.warning(f"O texto tem {len(words)} palavras. Por favor, reduza para no máximo 500.")
    else:
        # Normalizar texto
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)

        # Processar texto com spaCy
        doc = nlp(text)

        # Filtrar palavras
        filtered_words = [
            token.text for token in doc
            if token.pos_ not in ["VERB", "CCONJ", "SCONJ", "ADP", "PRON"]
            and token.text not in nlp.Defaults.stop_words
        ]

        filtered_text = " ".join(filtered_words)

        # Gerar nuvem de palavras
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(filtered_text)

        # Exibir nuvem
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)

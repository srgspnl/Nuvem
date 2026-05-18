import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import spacy

# Configuração da página do Streamlit
st.set_page_config(page_title="Nuvem de Palavras Pro", layout="wide")

# 1. Carregamento do modelo spaCy com Cache para performance
@st.cache_resource
def load_nlp():
    # Certifique-se de incluir 'pt_core_news_sm' no seu arquivo requirements.txt
    try:
        return spacy.load("pt_core_news_sm")
    except OSError:
        # Fallback caso não esteja instalado localmente no ambiente de teste
        import spacy.cli
        spacy.cli.download("pt_core_news_sm")
        return spacy.load("pt_core_news_sm")

nlp = load_nlp()

st.title("☁️ Gerador Avançado de Nuvem de Palavras")
st.markdown("Analise a frequência de termos textuais aplicando filtros linguísticos avançados em tempo real.")

# Inicializar estruturas de controle na barra lateral
st.sidebar.header("🛠️ Configurações de Filtros")

# Controles para omitir classes gramaticais voluntariamente
omit_verbs = st.sidebar.checkbox("Omitir Verbos", value=True)
omit_adjectives = st.sidebar.checkbox("Omitir Adjetivos", value=False)
omit_nouns = st.sidebar.checkbox("Omitir Substantivos (Nouns)", value=False)
omit_adverbs = st.sidebar.checkbox("Omitir Advérbios", value=False)

# Campo para lista de palavras customizadas a omitir
st.sidebar.markdown("---")
custom_stopwords_input = st.sidebar.text_area(
    "Palavras personalizadas para omitir:",
    placeholder="Ex: empresa, portanto, assim (separe por vírgula ou espaço)"
)

# Processando as stopwords customizadas
custom_stopwords = set()
if custom_stopwords_input:
    # Captura as palavras limpando espaços em branco e convertendo para minúsculo
    custom_stopwords = {word.strip().lower() for word in custom_stopwords_input.replace(",", " ").split() if word.strip()}

# Área principal de entrada de texto
text = st.text_area("Cole seu texto abaixo (máximo 500 palavras):", height=250)

if text:
    words = text.split()
    if len(words) > 500:
        st.warning(f"⚠️ O texto atual contém {len(words)} palavras. Por favor, reduza para no máximo 500 para otimizar o processamento.")
    else:
        # 2. Processamento robusto com o pipeline do spaCy (Sem regex agressivo antes)
        # O spaCy lida nativamente com maiúsculas/minúsculas através do token.lemma_ ou token.text.lower()
        doc = nlp(text)

        # 3. Construção da lista de classes gramaticais banidas sistematicamente
        # Preposições (ADP), Conectivos (CCONJ/SCONJ), Artigos/Determinantes (DET), Pronomes (PRON)
        pos_blacklist = ["ADP", "CCONJ", "SCONJ", "DET", "PRON", "PUNCT", "SYM", "SPACE"]

        # Adicionando filtros dinâmicos baseados nos checkboxes do usuário
        if omit_verbs:
            pos_blacklist.append("VERB")
            pos_blacklist.append("AUX")  # Verbos auxiliares
        if omit_adjectives:
            pos_blacklist.append("ADJ")
        if omit_nouns:
            pos_blacklist.append("NOUN")
            pos_blacklist.append("PROPN") # Nomes próprios
        if omit_adverbs:
            pos_blacklist.append("ADV")

        # 4. Filtragem inteligente dos tokens
        filtered_words = []
        for token in doc:
            token_text_lower = token.text.lower()
            
            # Validações: Classe gramatical, Stopwords nativas e Stopwords customizadas
            if (token.pos_ not in pos_blacklist and 
                token_text_lower not in nlp.Defaults.stop_words and 
                token_text_lower not in custom_stopwords and
                len(token_text_lower) > 1): # Ignora letras isoladas remanescentes
                
                filtered_words.append(token.text)

        # Reconecta as palavras filtradas para alimentar a nuvem
        filtered_text = " ".join(filtered_words)

        if filtered_text.strip() == "":
            st.error("❌ Nenhuma palavra restou após a aplicação dos filtros configurados. Ajuste a barra lateral.")
        else:
            # 5. Geração e renderização da Nuvem de Palavras
            with st.spinner("Gerando nuvem de palavras..."):
                wordcloud = WordCloud(
                    width=1000, 
                    height=500, 
                    background_color='white',
                    colormap='viridis',
                    max_words=100
                ).generate(filtered_text)

                # Exibição gráfica tratada no Streamlit
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)
                
                st.success(f"Nuvem gerada com sucesso! {len(filtered_words)} palavras filtradas analisadas.")
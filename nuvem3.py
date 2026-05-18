import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import spacy

# Configuração da página do Streamlit
st.set_page_config(page_title="Nuvem de Palavras Pro", layout="wide")

# Carregamento do modelo spaCy usando o cache nativo do Streamlit
@st.cache_resource
def load_nlp():
    # Como o modelo está no requirements.txt, o carregamento é direto e seguro
    return spacy.load("pt_core_news_sm")

nlp = load_nlp()

st.title("☁️ Gerador Avançado de Nuvem de Palavras")
st.markdown("Analise a frequência de termos textuais aplicando filtros linguísticos avançados em tempo real.")

# Inicializar estruturas de controle na barra lateral (Sidebar)
st.sidebar.header("🛠️ Configurações de Filtros")

# Controles interativos para ocultar classes gramaticais voluntariamente
omit_verbs = st.sidebar.checkbox("Omitir Verbos e Auxiliares", value=True)
omit_adjectives = st.sidebar.checkbox("Omitir Adjetivos", value=False)
omit_nouns = st.sidebar.checkbox("Omitir Substantivos / Nomes", value=False)
omit_adverbs = st.sidebar.checkbox("Omitir Advérbios", value=False)

# Campo para lista de palavras customizadas (Stopwords personalizadas)
st.sidebar.markdown("---")
custom_stopwords_input = st.sidebar.text_area(
    "Palavras personalizadas para omitir:",
    placeholder="Ex: empresa, portanto, assim (separe por vírgula ou espaço)"
)

# Processando as palavras personalizadas inseridas pelo usuário
custom_stopwords = set()
if custom_stopwords_input:
    # Limpa espaços em branco e padroniza em caixa baixa
    custom_stopwords = {word.strip().lower() for word in custom_stopwords_input.replace(",", " ").split() if word.strip()}

# Área principal para entrada do texto de análise
text = st.text_area("Cole seu texto abaixo (máximo 500 palavras):", height=250)

if text:
    words = text.split()
    if len(words) > 500:
        st.warning(f"⚠️ O texto atual contém {len(words)} palavras. Por favor, reduza para no máximo 500 para garantir a performance.")
    else:
        # Processamento léxico estruturado com o pipeline do spaCy
        doc = nlp(text)

        # Matriz fixa de exclusão (Sempre oculta pontuações, preposições, conjunções, artigos e pronomes)
        pos_blacklist = ["ADP", "CCONJ", "SCONJ", "DET", "PRON", "PUNCT", "SYM", "SPACE"]

        # Incrementa a lista negra baseado nas escolhas das caixas de seleção da barra lateral
        if omit_verbs:
            pos_blacklist.append("VERB")
            pos_blacklist.append("AUX")  # Omeia verbos auxiliares (ser, estar, ter...)
        if omit_adjectives:
            pos_blacklist.append("ADJ")
        if omit_nouns:
            pos_blacklist.append("NOUN")
            pos_blacklist.append("PROPN") # Omeia nomes próprios corporativos/geográficos
        if omit_adverbs:
            pos_blacklist.append("ADV")

        # Filtragem refinada de tokens baseada nas regras morfológicas e listas de exclusão
        filtered_words = []
        for token in doc:
            token_text_lower = token.text.lower()
            
            # Validações estruturais do token
            if (token.pos_ not in pos_blacklist and 
                token_text_lower not in nlp.Defaults.stop_words and 
                token_text_lower not in custom_stopwords and
                len(token_text_lower) > 1): # Ignora caracteres remanescentes isolados
                
                filtered_words.append(token.text)

        # Reconecta os tokens válidos em uma string única para o gerador
        filtered_text = " ".join(filtered_words)

        if filtered_text.strip() == "":
            st.error("❌ Nenhuma palavra restou após a aplicação dos filtros configurados. Ajuste os parâmetros na barra lateral.")
        else:
            # Renderização gráfica da nuvem de palavras
            with st.spinner("Gerando visualização gráfica..."):
                wordcloud = WordCloud(
                    width=1000, 
                    height=500, 
                    background_color='white',
                    colormap='viridis',
                    max_words=100
                ).generate(filtered_text)

                # Montagem do plot do Matplotlib integrado ao Streamlit
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)
                
                st.success(f"Nuvem gerada com sucesso! {len(filtered_words)} palavras elegíveis foram processadas.")
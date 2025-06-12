import streamlit as st
import sys
import os

# Adiciona o diretório raiz ao PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

# Configuração da página
st.set_page_config(
    page_title="Currículo Inteligente",
    page_icon="📊",
    layout="wide"
)

# Estilização customizada
st.markdown("""
<style>
/* Altera "Home" para "Menu Principal" */
section[data-testid="stSidebar"] .css-1d391kg {
    visibility: hidden;
}
section[data-testid="stSidebar"] .css-1d391kg:before {
    content: "Menu Principal";
    visibility: visible;
    font-size: 1.2rem;
    font-weight: bold;
    padding-left: 10px;
}

/* Remove padding e aumenta o espaçamento */
.main {
    padding: 3rem;
}

/* Estilo para blocos de menu */
.menu-item {
    padding: 1.5rem;
    border-radius: 12px;
    background-color: #f5f7fa;
    margin-bottom: 1.5rem;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
}
.menu-item:hover {
    background-color: #e6e9ef;
}

/* Remove o rodapé padrão */
footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# Título
st.title("Currículo Inteligente")
st.markdown("---")

# Conteúdo principal
with st.container():
    # Item 1
    st.markdown("""
    <div class="menu-item">
        <h2>1. Criar Nova Vaga</h2>
        <p>Cadastre uma nova vaga de emprego com suas especificações</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Acessar Cadastro de Vagas", key="btn_vagas"):
        st.switch_page("pages/1_📝_Cadastro_Vagas.py")

    # Item 2
    st.markdown("""
    <div class="menu-item">
        <h2>2. Importar Currículos</h2>
        <p>Carregue um ou mais currículos para análise</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Acessar Importação de Currículos", key="btn_curriculos"):
        st.switch_page("pages/2_📄_Importar_Curriculos.py")

# Remove rodapé extra
st.markdown("""<style>footer {visibility: hidden;}</style>""", unsafe_allow_html=True)

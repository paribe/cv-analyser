import streamlit as st
import sys
import os

# Adicionar o diretório raiz ao PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

st.set_page_config(
    page_title="CV Analyzer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 CV Analyzer")
st.markdown("---")

# Container principal com estilo
with st.container():
    st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .menu-item {
        padding: 1rem;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 1rem 0;
        cursor: pointer;
    }
    .menu-item:hover {
        background-color: #e0e2e6;
    }
    </style>
    """, unsafe_allow_html=True)

    # Opção 1: Criar Vaga
    st.markdown("""
    <div class="menu-item">
        <h2>1. 📝 Criar Nova Vaga</h2>
        <p>Cadastre uma nova vaga de emprego com suas especificações</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Acessar Cadastro de Vagas", key="btn_vagas"):
        st.switch_page("pages/1_📝_Cadastro_Vagas.py")

    # Opção 2: Carregar Currículos
    st.markdown("""
    <div class="menu-item">
        <h2>2. 📄 Importar Currículos</h2>
        <p>Carregue um ou mais currículos para análise</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Acessar Importação de Currículos", key="btn_curriculos"):
        st.switch_page("pages/2_📄_Importar_Curriculos.py")

# Rodapé
st.markdown("---")
st.markdown("Desenvolvido com ❤️ usando Streamlit") 
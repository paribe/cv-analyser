import streamlit as st
import sys
import os
import uuid

# Adicionar o diretório raiz ao PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, root_dir)

from analyze.models.job import Job
from analyze.database import AnalyzeDatabase

st.set_page_config(
    page_title="Cadastro de Vagas - Currículo Inteligente",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Cadastro de Vagas")
st.markdown("---")

# Inicializar o banco de dados
database = AnalyzeDatabase()

# Função para excluir vaga
def delete_job(job_id):
    database.delete_job_by_id(job_id)
    st.experimental_rerun()

# Formulário de cadastro
with st.form("form_vaga"):
    nome_vaga = st.text_input("Nome da Vaga")
    
    st.subheader("Atividades Principais")
    atividades = st.text_area("Descreva as atividades principais da vaga", height=200)
    
    st.subheader("Pré-requisitos")
    pre_requisitos = st.text_area("Liste os pré-requisitos da vaga", height=200)
    
    st.subheader("Diferenciais")
    diferenciais = st.text_area("Liste os diferenciais da vaga", height=200)
    
    submitted = st.form_submit_button("Salvar Vaga")
    
    if submitted:
        if nome_vaga and atividades and pre_requisitos and diferenciais:
            try:
                # Criar nova vaga
                job = Job(
                    id=str(uuid.uuid4()),
                    name=nome_vaga,
                    main_activities=atividades,
                    prerequisites=pre_requisitos,
                    differentials=diferenciais
                )
                
                # Salvar no banco de dados
                database.jobs.insert(job.model_dump())
                st.success("✅ Vaga cadastrada com sucesso!")
                st.experimental_rerun() # Recarregar a página para mostrar a nova vaga
                
            except Exception as e:
                st.error(f"❌ Erro ao cadastrar vaga: {str(e)}")
        else:
            st.warning("⚠️ Por favor, preencha todos os campos!")

# Lista de vagas cadastradas
st.markdown("---")
st.subheader("Vagas Cadastradas")

# Buscar vagas no banco de dados usando o método correto do TinyDB
vagas = database.jobs.all()

if vagas:
    for vaga in vagas:
        col1, col2 = st.columns([3, 1])
        with col1:
            with st.expander(f"📋 {vaga['name']}"):
                st.markdown("**Atividades Principais:**")
                st.write(vaga['main_activities'])
                st.markdown("**Pré-requisitos:**")
                st.write(vaga['prerequisites'])
                st.markdown("**Diferenciais:**")
                st.write(vaga['differentials'])
        with col2:
            if st.button("Excluir", key=f"delete_{vaga['id']}"):
                delete_job(vaga['id'])

else:
    st.info("Nenhuma vaga cadastrada ainda.")

# Botão para voltar ao menu principal
if st.button("Voltar ao Menu Principal"):
    st.switch_page("Home.py") 
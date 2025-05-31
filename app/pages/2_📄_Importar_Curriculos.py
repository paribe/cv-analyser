import streamlit as st
import sys
import os
import uuid
import tempfile
import pandas as pd

# Adicionar o diretório raiz ao PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, root_dir)

from analyze.database import AnalyzeDatabase
from analyze.helper import read_uploaded_file, extract_data_analysis
from analyze.ai import GroqClient
from analyze.models.resum import Resum
from analyze.models.file import File
from analyze.models.analysis import Analysis

def process_cv_file(file_path, job_name):
    """Processa um arquivo de currículo e salva os resultados no banco de dados"""
    try:
        # Inicializar o banco de dados e o cliente de IA
        database = AnalyzeDatabase()
        ai = GroqClient()
        
        # Obter a vaga do banco de dados
        job = database.get_job_by_name(job_name)
        if not job:
            raise ValueError(f"Vaga '{job_name}' não encontrada no banco de dados.")
        
        # Ler o conteúdo do arquivo PDF
        content = read_uploaded_file(file_path)
        
        # Gerar resumo do currículo
        resum = ai.resume_cv(content)
        
        # Gerar opinião sobre o currículo
        opnion = ai.generate_opnion(content, job)
        
        # Calcular pontuação
        score = ai.generate_score(resum, job)
        
        # Extrair dados da análise
        analysis_id = str(uuid.uuid4())
        analysis = extract_data_analysis(resum, job.get('id'), analysis_id, score)
        
        # Criar registros no banco de dados
        resum_schema = Resum(
            id=str(uuid.uuid4()),
            job_id=job.get('id'),
            content=resum,
            file=str(file_path),
            opnion=opnion
        )
        
        file_schema = File(
            file_id=str(uuid.uuid4()),
            job_id=job.get('id')
        )
        
        # Salvar no banco de dados
        database.resums.insert(resum_schema.model_dump())
        database.files.insert(file_schema.model_dump())
        database.analysis.insert(analysis.model_dump())
        
        # Retornar os dados processados
        return {
            "file_name": os.path.basename(file_path),
            "name": analysis.name,
            "score": analysis.score,
            "resumo": resum_schema.content,
            "analise": resum_schema.opnion
        }
        
    except Exception as e:
        st.error(f"❌ Erro ao processar currículo {os.path.basename(file_path)}: {str(e)}")
        return {
            "file_name": os.path.basename(file_path),
            "name": "Erro",
            "score": "N/A",
            "resumo": f"Erro ao processar: {str(e)}",
            "analise": "N/A"
        }

st.set_page_config(
    page_title="Importar Currículos - CV Analyzer",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Importar Currículos")
st.markdown("---")

# Inicializar o banco de dados
database = AnalyzeDatabase()

# Selecionar vaga
vagas = database.jobs.all()
if not vagas:
    st.error("❌ Nenhuma vaga cadastrada. Por favor, cadastre uma vaga primeiro.")
    if st.button("Ir para Cadastro de Vagas"):
        st.switch_page("pages/1_📝_Cadastro_Vagas.py")
else:
    # Criar lista de vagas para o selectbox
    vagas_list = [vaga['name'] for vaga in vagas]
    vaga_selecionada = st.selectbox("Selecione a vaga para análise:", vagas_list)
    
    # Upload de arquivos
    uploaded_files = st.file_uploader(
        "Selecione um ou mais currículos (PDF)",
        type=['pdf'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("Analisar Currículos"):
            # Criar barra de progresso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            processed_results = []
            
            # Processar cada arquivo
            for i, uploaded_file in enumerate(uploaded_files):
                # Salvar arquivo temporariamente
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                # Processar o currículo e armazenar o resultado
                result = process_cv_file(tmp_path, vaga_selecionada)
                processed_results.append(result)
                
                # Remover arquivo temporário
                os.unlink(tmp_path)
                
                # Atualizar progresso
                progress = (i + 1) / len(uploaded_files)
                progress_bar.progress(progress)
            
            # Finalizar processamento
            status_text.text("✅ Processamento concluído!")
            st.success("Todos os currículos foram processados com sucesso!")
            
            # Exibir os resultados detalhados
            st.markdown("---")
            st.subheader("Resultados Detalhados da Análise")
            
            if processed_results:
                for result in processed_results:
                    st.markdown(f"**Arquivo: {result['file_name']}**")
                    st.markdown(f"**Nome do Candidato: {result['name']}**")
                    st.markdown(f"**Pontuação: {result['score']:.2f}**")
                    st.markdown("**Resumo Gerado:**")
                    st.write(result['resumo'])
                    st.markdown("**Análise Gerada:**")
                    st.write(result['analise'])
                    st.markdown("---")

                    print (result['name'])

            else:
                st.info("Nenhum resultado para exibir.")

# Botão para voltar ao menu principal
if st.button("Voltar ao Menu Principal"):
    st.switch_page("Home.py") 
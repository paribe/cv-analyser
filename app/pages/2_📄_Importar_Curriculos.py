import streamlit as st
import sys
import os
import uuid
import tempfile
import pandas as pd
import time

# Adicionar o diretório raiz ao PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, root_dir)

from analyze.database import AnalyzeDatabase
from analyze.helper import read_uploaded_file, extract_data_analysis
#from analyze.ai import GroqClient
from analyze.models.resum import Resum
from analyze.models.file import File
from analyze.models.analysis import Analysis
from analyze.ai import OpenAIClient

def process_cv_file(file_path, job_name, file_index, total_files):
    """Processa um arquivo de currículo e salva os resultados no banco de dados"""
    try:
        # Mostrar qual arquivo está sendo processado
        file_name = os.path.basename(file_path)
        st.info(f"📄 Processando arquivo {file_index}/{total_files}: {file_name}")
        
        # Inicializar o banco de dados e o cliente de IA
        database = AnalyzeDatabase()
        ai = OpenAIClient()

        # Obter a vaga do banco de dados
        job = database.get_job_by_name(job_name)
        if not job:
            raise ValueError(f"Vaga '{job_name}' não encontrada no banco de dados.")
        
        # Ler o conteúdo do arquivo PDF
        with st.spinner("📖 Lendo conteúdo do arquivo PDF..."):
            content = read_uploaded_file(file_path)
        
        # Gerar resumo do currículo
        with st.spinner("📝 Gerando resumo do currículo..."):
            resum = ai.resume_cv(content)
        
        # Gerar opinião sobre o currículo
        with st.spinner("🔍 Analisando adequação à vaga..."):
            opnion = ai.generate_opnion(content, job)
        
        # Calcular pontuação
        with st.spinner("📊 Calculando pontuação de compatibilidade..."):
            score = ai.generate_score(resum, job)
        
        # Extrair dados da análise
        with st.spinner("💾 Salvando dados no banco..."):
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
        
        # Mostrar sucesso para este arquivo
        st.success(f"✅ {file_name} processado com sucesso!")
        
        # Retornar os dados processados
        return {
            "file_name": os.path.basename(file_path),
            "name": analysis.name,
            "score": analysis.score,
            "resumo": resum_schema.content,
            "analise": resum_schema.opnion
        }
        
    except Exception as e:
        error_msg = f"❌ Erro ao processar currículo {os.path.basename(file_path)}: {str(e)}"
        st.error(error_msg)
        return {
            "file_name": os.path.basename(file_path),
            "name": "Erro",
            "score": "N/A",
            "resumo": f"Erro ao processar: {str(e)}",
            "analise": "N/A"
        }

st.set_page_config(
    page_title="Importar Currículos - Currículo Inteligente",
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
        # Mostrar informações sobre os arquivos carregados
        st.info(f"📁 {len(uploaded_files)} arquivo(s) carregado(s) para análise")
        
        if st.button("🚀 Analisar Currículos", type="primary"):
            # Container para as mensagens de processamento
            processing_container = st.container()
            
            with processing_container:
                # Mensagem inicial
                st.markdown("### 🔄 Processamento Iniciado")
                st.markdown("---")
                
                # Barra de progresso principal
                main_progress = st.progress(0)
                status_placeholder = st.empty()
                
                # Container para mensagens individuais
                messages_container = st.container()
                
                with st.spinner("⏳ Aguarde... Processando currículos..."):
                    processed_results = []
                    total_files = len(uploaded_files)
                    
                    # Atualizar status inicial
                    status_placeholder.markdown(f"**📊 Progresso geral: 0/{total_files} arquivos processados**")
                    
                    # Processar cada arquivo
                    for i, uploaded_file in enumerate(uploaded_files):
                        current_file = i + 1
                        
                        # Atualizar status geral
                        status_placeholder.markdown(f"**📊 Progresso geral: {i}/{total_files} arquivos processados**")
                        
                        # Salvar arquivo temporariamente
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name
                        
                        # Processar o currículo dentro do container de mensagens
                        with messages_container:
                            result = process_cv_file(tmp_path, vaga_selecionada, current_file, total_files)
                            processed_results.append(result)
                        
                        # Remover arquivo temporário
                        os.unlink(tmp_path)
                        
                        # Atualizar progresso principal
                        progress = (current_file) / total_files
                        main_progress.progress(progress)
                        
                        # Pequena pausa para melhor experiência visual
                        time.sleep(0.5)
                    
                    # Atualizar status final
                    status_placeholder.markdown(f"**🎉 Concluído: {total_files}/{total_files} arquivos processados**")
                
                # Mensagem de conclusão
                st.markdown("---")
                st.success("🎉 Todos os currículos foram processados com sucesso!")
                
                # Balões de celebração
                st.balloons()
            
            # Seção de resultados detalhados
            st.markdown("---")
            st.markdown("### 📋 Resultados Detalhados da Análise")
            st.markdown("---")
            
            if processed_results:
                # Filtros opcionais
                col1, col2 = st.columns([1, 1])
                with col1:
                    show_only_success = st.checkbox("Mostrar apenas processamentos bem-sucedidos")
                with col2:
                    sort_by_score = st.checkbox("Ordenar por pontuação (maior para menor)")
                
                # Filtrar e ordenar resultados
                display_results = processed_results.copy()
                
                if show_only_success:
                    display_results = [r for r in display_results if r['name'] != 'Erro']
                
                if sort_by_score:
                    display_results.sort(
                        key=lambda x: x['score'] if isinstance(x['score'], (int, float)) else 0, 
                        reverse=True
                    )
                
                # Exibir resultados
                for idx, result in enumerate(display_results, 1):
                    with st.expander(f"📄 {idx}. {result['file_name']} - {result['name']}", expanded=False):
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.markdown(f"**👤 Nome do Candidato:** {result['name']}")
                            score = result['score']
                            if isinstance(score, (int, float)):
                                # Colorir score baseado na pontuação
                                if score >= 80:
                                    st.markdown(f"**📊 Pontuação:** :green[{score:.2f}/100] 🔥")
                                elif score >= 60:
                                    st.markdown(f"**📊 Pontuação:** :orange[{score:.2f}/100] ⚡")
                                else:
                                    st.markdown(f"**📊 Pontuação:** :red[{score:.2f}/100] 📉")
                            else:
                                st.markdown(f"**📊 Pontuação:** {score}")
                        
                        with col2:
                            st.markdown(f"**📁 Arquivo:** {result['file_name']}")
                            
                            # Indicador visual de status
                            if result['name'] == 'Erro':
                                st.markdown("**Status:** :red[❌ Erro no processamento]")
                            else:
                                st.markdown("**Status:** :green[✅ Processado com sucesso]")
                        
                        st.markdown("---")
                        
                        # Tabs para organizar melhor o conteúdo
                        tab1, tab2 = st.tabs(["📝 Resumo", "🔍 Análise"])
                        
                        with tab1:
                            st.markdown("**Resumo Gerado:**")
                            st.write(result['resumo'])
                        
                        with tab2:
                            st.markdown("**Análise Detalhada:**")
                            st.write(result['analise'])

                # Estatísticas resumidas
                st.markdown("---")
                st.markdown("### 📈 Estatísticas do Processamento")
                
                col1, col2, col3, col4 = st.columns(4)
                
                successful_results = [r for r in processed_results if r['name'] != 'Erro']
                failed_results = [r for r in processed_results if r['name'] == 'Erro']
                
                with col1:
                    st.metric("Total de Arquivos", len(processed_results))
                
                with col2:
                    st.metric("Processados com Sucesso", len(successful_results))
                
                with col3:
                    st.metric("Erros", len(failed_results))
                
                with col4:
                    if successful_results:
                        scores = [r['score'] for r in successful_results if isinstance(r['score'], (int, float))]
                        if scores:
                            avg_score = sum(scores) / len(scores)
                            st.metric("Pontuação Média", f"{avg_score:.1f}")
                        else:
                            st.metric("Pontuação Média", "N/A")
                    else:
                        st.metric("Pontuação Média", "N/A")

            else:
                st.info("Nenhum resultado para exibir.")

# Botão para voltar ao menu principal
st.markdown("---")
if st.button("🏠 Voltar ao Menu Principal"):
    st.switch_page("Home.py")
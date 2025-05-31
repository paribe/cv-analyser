import re, uuid, os
import PyPDF2
from analyze.models.analysis import Analysis

def get_pdf_paths(directory):
    """Retorna uma lista de caminhos para arquivos PDF no diretório especificado"""
    pdf_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_paths.append(os.path.join(root, file))
    return pdf_paths

def read_uploaded_file(file_path):
    """Lê o conteúdo de um arquivo PDF e retorna como texto"""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        raise Exception(f"Erro ao ler arquivo PDF: {str(e)}")

print("🔹 Checando se nome está presente no resumo...")

def extract_data_analysis(resum, job_id, analysis_id, score):
    """Extrai dados da análise do currículo"""
    try:
        # Aqui você pode adicionar lógica para extrair mais informações do resumo
        # Por enquanto, vamos criar uma análise básica
        analysis = Analysis(
            id=analysis_id,
            job_id=job_id,
            score=score,
            name="Candidato",  # Isso pode ser extraído do resumo
            status="Processado"
        )
        return analysis
    except Exception as e:
        raise ValueError(f"Erro ao extrair dados da análise: {str(e)}")

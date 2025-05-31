import uuid
from helper import get_pdf_paths, read_uploaded_file, extract_data_analysis
from database import AnalyzeDatabase
from ai import GroqClient
from models.resum import Resum
from models.file import File

# Inicializar a conexão com o banco de dados de análise
database = AnalyzeDatabase()

# Obter a vaga de emprego a partir do banco de dados
job_name = 'Data Engineer'  # Pode ser parametrizado futuramente

job = database.get_job_by_name(job_name)

if not job:
    print(f"❌ Vaga '{job_name}' não encontrada no banco de dados.")
    exit(1)

# Inicializar o cliente de IA para processar os currículos
ai = GroqClient()

# Obter os caminhos dos arquivos PDF contendo os currículos
cv_paths = get_pdf_paths('curriculos')

# Iterar sobre cada caminho de arquivo de currículo na lista
for path in cv_paths:
    print(f"\n🔹 Processando arquivo: {path}")

    try:
        # Ler o conteúdo do arquivo PDF de currículo
        content = read_uploaded_file(path)
        
        # Usar o modelo de IA para resumir o conteúdo do currículo
        resum = ai.resume_cv(content)
        print("🔹 Resumo gerado:\n", resum)
        
        # Gerar uma opinião sobre o currículo com base na vaga de emprego
        opnion = ai.generate_opnion(content, job)
        print("🔹 Opinião gerada:\n", opnion)
        
        # Calcular uma pontuação para o currículo com base no resumo e nos requisitos da vaga
        score = ai.generate_score(resum, job)
        print("🔹 Pontuação gerada:", score)
        
        # Extrair a análise dos dados utilizando o resumo e informações adicionais
        try:
            analysis = extract_data_analysis(resum, job.get('id'), str(uuid.uuid4()), score)
        except ValueError:
            # Suprimir mensagem de erro e continuar para próximo currículo
            continue
        
        # Agora verificamos se o nome extraído está presente e válido
        name = getattr(analysis, 'name', None)
        if not name or name.strip() == "":
            print("⚠️ ATENÇÃO: Nome do candidato não encontrado na análise! Continuando com o processamento...")
        
        # Criar uma instância do schema Resum para armazenar os dados do resumo
        resum_schema = Resum(
            id=str(uuid.uuid4()),
            job_id=job.get('id'),
            content=resum,
            file=str(path),
            opnion=opnion
        )
        
        # Criar uma instância do schema File para armazenar os dados do arquivo
        file = File(
            file_id=str(uuid.uuid4()),
            job_id=job.get('id')
        )
        
        # Inserir os dados gerados no banco de dados
        database.resums.insert(resum_schema.model_dump())
        database.analysis.insert(analysis.model_dump())
        database.files.insert(file.model_dump())

        print(f"✅ Dados do currículo '{path}' inseridos com sucesso.\n")

    except Exception as e:
        print(f"❌ Erro inesperado ao processar o arquivo '{path}': {e}")
        print("⚠️ Pulando para o próximo currículo.\n")
        continue

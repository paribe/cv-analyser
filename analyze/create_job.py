import uuid
from models.job import Job
from database import AnalyzeDatabase

database = AnalyzeDatabase()

name = 'Data Engineer'

activities = '''
Projetar e implementar pipelines de dados escaláveis e eficientes
Desenvolver e manter arquiteturas de dados em nuvem (AWS, GCP, Azure)
Construir sistemas ETL/ELT para processamento de grandes volumes de dados
Implementar soluções de streaming de dados em tempo real (Kafka, Kinesis)
Otimizar performance de consultas e bancos de dados (SQL, NoSQL)
Colaborar com cientistas de dados e analistas na preparação de dados
Implementar práticas de DataOps e versionamento de dados
Monitorar e garantir qualidade dos dados através de testes automatizados
Desenvolver APIs e microsserviços para acesso aos dados
Documentar arquiteturas e processos de engenharia de dados
'''

prerequisites = '''
Experiência comprovada como Data Engineer, Engenheiro de Dados ou função similar (3+ anos)
Domínio avançado de Python e SQL para manipulação e transformação de dados
Experiência com ferramentas de Big Data (Apache Spark, Hadoop, Airflow)
Conhecimento sólido de bancos de dados relacionais e NoSQL (PostgreSQL, MongoDB, Redis)
Experiência prática com plataformas de nuvem (AWS, GCP ou Azure)
Conhecimento de ferramentas de orquestração (Apache Airflow, Prefect, Dagster)
Experiência com containerização (Docker, Kubernetes)
Conhecimento de versionamento de código (Git) e metodologias ágeis
Habilidades de resolução de problemas complexos e pensamento analítico
Capacidade de trabalhar com grandes volumes de dados e sistemas distribuídos
'''

differentials = '''
Certificações em plataformas de nuvem (AWS Data Engineer, GCP Professional Data Engineer)
Experiência com ferramentas modernas de Data Stack (dbt, Snowflake, Databricks)
Conhecimento de Machine Learning e MLOps para deploy de modelos
Experiência com streaming de dados em tempo real (Apache Kafka, AWS Kinesis)
Conhecimento de Infrastructure as Code (Terraform, CloudFormation)
Experiência com Data Mesh e arquiteturas de dados modernas
Contribuições para projetos open source relacionados a dados
Conhecimento de linguagens complementares (Scala, Java, Go)
Experiência com ferramentas de observabilidade (Datadog, New Relic)
Experiência prévia em startups ou empresas de tecnologia
Conhecimento de LGPD/GDPR e práticas de governança de dados
'''

job = Job(
    id=str(uuid.uuid4()),
    name=name,
    main_activities=activities,
    prerequisites=prerequisites,
    differentials=differentials,
)

database.jobs.insert(job.model_dump())
import os
from openai import OpenAI

# Tentar carregar dotenv se disponível
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv não instalado, usar apenas variáveis de ambiente

class OpenAIClient:
    def __init__(self, api_key=None):
        """Initialize the OpenAI client"""
        # Obter API key de diferentes fontes
        if api_key:
            self.api_key = api_key
        elif os.getenv('OPENAI_API_KEY'):
            self.api_key = os.getenv('OPENAI_API_KEY')
        else:
            raise ValueError("""
            ❌ API key do OpenAI não encontrada!
            
            Configure de uma das formas:
            1. Variável de ambiente: export OPENAI_API_KEY="sua-api-key"
            2. Arquivo .env: OPENAI_API_KEY=sua-api-key
            3. Passar diretamente: OpenAIClient(api_key="sua-api-key")
            """)
        
        try:
            self.client = OpenAI(api_key=self.api_key)
            print("✅ Cliente OpenAI inicializado com sucesso!")
        except Exception as e:
            raise Exception(f"Erro ao inicializar cliente OpenAI: {str(e)}")
    
    def resume_cv(self, content):
        """Generate a resume summary from CV content"""
        try:
            if not content or content.strip() == "":
                return "Erro: Conteúdo do currículo está vazio"
            
            print("🔄 Gerando resumo do currículo...")
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "Você é um assistente de RH profissional. Resuma o seguinte conteúdo de currículo em português de forma clara e objetiva, destacando as principais qualificações, experiências e habilidades do candidato."
                    },
                    {
                        "role": "user", 
                        "content": f"Por favor, resuma este currículo de forma profissional:\n\n{content}"
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            result = response.choices[0].message.content
            print(f"✅ Resumo gerado! Tokens usados: {response.usage.total_tokens}")
            return result
            
        except Exception as e:
            error_msg = f"Erro ao gerar resumo: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def generate_opnion(self, content, job):
        """Generate an opinion about the CV for a specific job"""
        try:
            if not content or content.strip() == "":
                return "Erro: Conteúdo do currículo está vazio"
            
            job_name = job.get('name', 'Não especificada')
            job_description = job.get('description', 'Não especificada')
            
            prompt = f"""
            Analise o seguinte currículo em relação à vaga especificada:
            
            VAGA: {job_name}
            DESCRIÇÃO DA VAGA: {job_description}
            
            CURRÍCULO:
            {content}
            
            Forneça uma análise detalhada e profissional sobre:
            1. Adequação do candidato à vaga
            2. Pontos fortes do candidato
            3. Possíveis lacunas ou áreas de desenvolvimento
            4. Recomendação geral (contratar, não contratar, entrevista)
            
            Seja objetivo e construtivo na análise.
            """
            
            print("🔄 Gerando análise do currículo vs vaga...")
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em RH experiente. Analise currículos em relação às vagas de forma detalhada, profissional e construtiva em português."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            result = response.choices[0].message.content
            print(f"✅ Análise gerada! Tokens usados: {response.usage.total_tokens}")
            return result
            
        except Exception as e:
            error_msg = f"Erro ao gerar análise: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def generate_score(self, resume, job):
        """Generate a compatibility score between resume and job"""
        try:
            if not resume or resume.strip() == "":
                return 0.0
            
            job_name = job.get('name', 'Não especificada')
            job_description = job.get('description', 'Não especificada')
            
            prompt = f"""
            Com base no resumo do currículo e na descrição da vaga abaixo, 
            forneça uma pontuação de compatibilidade de 0 a 100:
            
            VAGA: {job_name}
            DESCRIÇÃO DA VAGA: {job_description}
            
            RESUMO DO CURRÍCULO:
            {resume}
            
            Critérios de avaliação:
            - Experiência relevante (30%)
            - Habilidades técnicas (25%)
            - Formação acadêmica (20%)
            - Adequação cultural/perfil (25%)
            
            Responda APENAS com o número da pontuação (exemplo: 75)
            """
            
            print("🔄 Calculando score de compatibilidade...")
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em RH. Forneça apenas uma pontuação numérica de 0 a 100 para compatibilidade currículo-vaga."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=10,
                temperature=0.3
            )
            
            # Extract numerical score
            score_text = response.choices[0].message.content.strip()
            print(f"🎯 Score bruto recebido: '{score_text}'")
            
            try:
                # Tentar converter diretamente
                score = float(score_text)
                # Garantir que está no range 0-100
                final_score = max(0.0, min(100.0, score))
                print(f"✅ Score final: {final_score}")
                return final_score
            except ValueError:
                # Se não conseguir converter, extrair números da resposta
                import re
                numbers = re.findall(r'\d+', score_text)
                if numbers:
                    score = float(numbers[0])
                    final_score = max(0.0, min(100.0, score))
                    print(f"✅ Score extraído: {final_score}")
                    return final_score
                print("⚠️ Não foi possível extrair score, retornando 0.0")
                return 0.0
                
        except Exception as e:
            error_msg = f"Erro ao gerar pontuação: {str(e)}"
            print(f"❌ {error_msg}")
            return 0.0
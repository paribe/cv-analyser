import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Carregar variáveis de ambiente
load_dotenv()

class GroqClient:
    def __init__(self):
        """Inicializar cliente Groq com modelo ativo"""
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY não encontrada no arquivo .env")
        
        self.client = ChatGroq(
            groq_api_key=self.api_key,
            model_name="llama3-8b-8192",  # Modelo ativo
            temperature=0.1,
            max_tokens=2048
        )
    
    def generate_response(self, prompt):
        """Gerar resposta usando Groq"""
        try:
            response = self.client.invoke(prompt)
            return response.content
        except Exception as e:
            return f"Erro na geração de resposta: {e}"
    
    def resume_cv(self, content):
        """Resumir currículo"""
        prompt = f"""
        Analise o seguinte currículo e crie um resumo profissional conciso em português brasileiro:

        CURRÍCULO:
        {content}

        INSTRUÇÕES:
        - Identifique as principais competências e experiências
        - Destaque formação acadêmica relevante
        - Mencione tecnologias e ferramentas conhecidas
        - Seja objetivo e profissional
        - Máximo 200 palavras

        RESUMO PROFISSIONAL:
        """
        
        return self.generate_response(prompt)
    
    def generate_opnion(self, cv_content, job):
        """Gerar opinião sobre adequação do candidato à vaga"""
        # Verificar se job não é None
        if job is None:
            return "Erro: Vaga não especificada para análise."
        
        job_name = job.get('name', 'Vaga não especificada')
        job_requirements = job.get('prerequisites', 'Requisitos não especificados')
        job_activities = job.get('main_activities', 'Atividades não especificadas')
        
        prompt = f"""
        Analise a adequação deste candidato para a vaga específica:

        VAGA: {job_name}
        
        ATIVIDADES PRINCIPAIS:
        {job_activities}
        
        REQUISITOS DA VAGA:
        {job_requirements}

        CURRÍCULO DO CANDIDATO:
        {cv_content[:3000]}  # Limitar tamanho

        INSTRUÇÕES:
        - Avalie se o candidato atende aos requisitos principais
        - Identifique pontos fortes que se alinham com a vaga
        - Mencione possíveis gaps ou pontos de atenção
        - Destaque experiências mais relevantes para esta posição
        - Seja honesto, construtivo e específico
        - Máximo 300 palavras

        OPINIÃO SOBRE A ADEQUAÇÃO:
        """
        
        return self.generate_response(prompt)
    
    def generate_score(self, resume, job):
        """Gerar pontuação de 0 a 100 para o candidato"""
        # Verificar se job não é None
        if job is None:
            print("⚠️ Vaga não especificada para scoring. Usando score padrão.")
            return 50.0
            
        job_name = job.get('name', 'Vaga não especificada')
        job_requirements = job.get('prerequisites', 'Requisitos não especificados')
        
        prompt = f"""
        Avalie este candidato para a vaga e dê uma nota de 0 a 100:

        VAGA: {job_name}
        
        REQUISITOS OBRIGATÓRIOS:
        {job_requirements}

        RESUMO DO CANDIDATO:
        {resume}

        CRITÉRIOS DE AVALIAÇÃO:
        - Experiência técnica relevante (40 pontos)
        - Formação adequada (20 pontos)
        - Habilidades específicas da vaga (25 pontos)
        - Adequação geral e fit cultural (15 pontos)

        INSTRUÇÕES IMPORTANTES:
        - Seja rigoroso na avaliação
        - Considere apenas experiências comprovadas
        - Retorne APENAS um número entre 0 e 100
        - Exemplo de resposta válida: 75
        - NÃO adicione texto, explicações ou pontos
        - APENAS O NÚMERO

        PONTUAÇÃO (apenas número):
        """
        
        result_raw = self.generate_response(prompt)
        return self.extract_score_from_result(result_raw)
    
    def extract_score_from_result(self, result_raw):
        """Extrair pontuação numérica da resposta da IA com validação robusta"""
        try:
            # Limpar a string
            cleaned_result = str(result_raw).strip()
            
            # Método 1: Procurar por números inteiros (mais comum)
            integer_match = re.search(r'\b(\d{1,3})\b', cleaned_result)
            if integer_match:
                score = int(integer_match.group(1))
                if 0 <= score <= 100:
                    return float(score)
            
            # Método 2: Procurar por números decimais
            decimal_match = re.search(r'\b(\d{1,2}(?:\.\d{1,2})?)\b', cleaned_result)
            if decimal_match:
                score_str = decimal_match.group(1)
                if score_str and score_str != '.':
                    score = float(score_str.replace(',', '.'))
                    if 0 <= score <= 100:
                        return score
            
            # Método 3: Procurar padrões específicos
            patterns = [
                r'pontuação[:\s]*(\d{1,3})',
                r'nota[:\s]*(\d{1,3})',
                r'score[:\s]*(\d{1,3})',
                r'(\d{1,3})[:\s]*pontos?',
                r'(\d{1,3})%',
                r'(\d{1,3})/100'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, cleaned_result, re.IGNORECASE)
                if match:
                    score = int(match.group(1))
                    if 0 <= score <= 100:
                        return float(score)
            
            # Método 4: Buscar qualquer sequência de dígitos
            all_numbers = re.findall(r'\d+', cleaned_result)
            for num_str in all_numbers:
                if num_str:
                    score = int(num_str)
                    if 0 <= score <= 100:
                        return float(score)
            
            # Se nada funcionou, retornar score padrão
            print(f"⚠️ Não foi possível extrair pontuação de: '{cleaned_result}'. Usando score padrão.")
            return 50.0
            
        except Exception as e:
            print(f"❌ Erro ao extrair pontuação: {e}. Resultado: '{result_raw}'. Usando score padrão.")
            return 50.0
        

 # analyze/ai.py
import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class OpenAIClient:
    def resume_cv(self, content):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um especialista em RH que resume currículos."},
                {"role": "user", "content": f"Resuma o seguinte currículo:\n\n{content}"}
            ]
        )
        return response['choices'][0]['message']['content']

    def generate_opnion(self, content, job):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um recrutador avaliando currículos com base em uma vaga de emprego."},
                {"role": "user", "content": f"Avalie esse currículo com base nesta vaga:\n\nVaga: {job['description']}\n\nCurrículo:\n{content}"}
            ]
        )
        return response['choices'][0]['message']['content']

    def generate_score(self, resum, job):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um avaliador que dá uma nota entre 0 e 100 para um currículo."},
                {"role": "user", "content": f"Dê uma nota de 0 a 100 para esse resumo de currículo considerando a vaga:\n\nResumo:\n{resum}\n\nVaga:\n{job['description']}"}
            ]
        )
        score_text = response['choices'][0]['message']['content']
        try:
            return float(score_text.strip())
        except:
            return 0.0
       
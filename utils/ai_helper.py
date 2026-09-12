import os
import streamlit as st
import requests
import json

def get_api_key():
    """Recupera a chave de API da sessão, secrets ou variáveis de ambiente de forma segura."""
    if "user_gemini_key" in st.session_state and st.session_state["user_gemini_key"]:
        return st.session_state["user_gemini_key"].strip()
    
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            return str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        pass
        
    return os.getenv("GEMINI_API_KEY", "")

def render_api_key_sidebar():
    """Renderiza um campo opcional na barra lateral para o aluno/professor inserir a chave."""
    with st.sidebar.expander("🔑 Configurar Chave de IA (Opcional)", expanded=False):
        current_key = get_api_key()
        user_key = st.text_input(
            "Google Gemini API Key:",
            value=st.session_state.get("user_gemini_key", ""),
            type="password",
            placeholder="AIzaSy...",
            help="Insira sua chave gratuita do Google AI Studio para respostas em tempo real."
        )
        if user_key != st.session_state.get("user_gemini_key", ""):
            st.session_state["user_gemini_key"] = user_key
            st.rerun()

        if current_key:
            st.caption("✅ Motor de IA Conectado: **Google Gemini Ativo**")
        else:
            st.caption("⚡ Motor Ativo: **Simulador Inteligente Integrado (Sem Custo)**")

def generate_text_ai(prompt: str, system_instruction: str = "", chat_history: list = None) -> str:
    """
    Gera texto usando a API REST do Google Gemini (alta compatibilidade e robustez).
    Suporta histórico de conversa para manter contexto no chatbot.
    """
    api_key = get_api_key()
    
    if api_key:
        # Tenta os modelos Gemini mais recentes e estáveis
        models_to_try = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
        
        for model_name in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            
            # Monta o payload no formato oficial da API do Gemini
            contents = []
            
            # Se houver histórico de chat, adiciona as mensagens anteriores
            if chat_history and len(chat_history) > 1:
                for msg in chat_history[:-1]: # Pega mensagens anteriores
                    role = "user" if msg.get("role") == "user" else "model"
                    contents.append({
                        "role": role,
                        "parts": [{"text": msg.get("content", "")}]
                    })
            
            # Adiciona a mensagem atual
            contents.append({
                "role": "user",
                "parts": [{"text": prompt}]
            })
            
            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 800
                }
            }
            
            if system_instruction:
                payload["systemInstruction"] = {
                    "parts": [{"text": system_instruction}]
                }
                
            try:
                resp = requests.post(url, json=payload, timeout=15)
                
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"]
                else:
                    error_data = resp.json().get("error", {})
                    error_msg = error_data.get("message", f"Status code {resp.status_code}")
                    # Se for erro de autenticação ou quota, avisa o usuário
                    if resp.status_code in [400, 403, 429]:
                        st.error(f"⚠️ Erro na API do Gemini: {error_msg}. Verifique sua chave.")
                        break
            except Exception as e:
                continue

    return None

def generate_chatbot_offline_reply(user_input: str, empresa: str, nome_bot: str, tom_bot: str, history: list) -> str:
    """
    Motor de diálogo heurístico com memória de contexto e variação dinâmica de respostas.
    """
    u_lower = user_input.lower().strip()
    
    # 1. Saudações e Cumprimentos
    if any(u_lower.startswith(w) or u_lower == w for w in ["ola", "olá", "oi", "bom dia", "boa tarde", "boa noite", "e ai", "e aí", "opa"]):
        if len(history) <= 2:
            return f"Olá! Seja muito bem-vindo(a) à {empresa}! 😊 Sou a {nome_bot}. Em que posso te ajudar hoje? Você procura informações sobre nossos cursos, valores ou horários das turmas?"
        else:
            return f"Olá novamente! Como posso te ajudar a avançar na sua formação ou tirar dúvidas sobre a {empresa}?"
            
    # 2. Preços e Formas de Pagamento
    if any(w in u_lower for w in ["preco", "preço", "valor", "custa", "investimento", "pagamento", "cartao", "cartão", "parcela", "desconto", "boleto"]):
        return f"O investimento para o curso de Marketing Digital com IA é de R$ 490,00, podendo ser parcelado em até 10x sem juros no cartão de crédito! 💳 Para pagamentos à vista via Pix, temos uma condição especial com 5% de desconto. Gostaria de garantir sua vaga com essa condição?"

    # 3. Horários, Datas e Início das Turmas
    if any(w in u_lower for w in ["data", "quando", "inicio", "início", "horario", "horário", "dias", "turno", "noite"]):
        return f"Nossas turmas acontecem de segunda a quinta-feira, das 19h às 22h, totalizando 30 horas práticas de capacitação no laboratório. A próxima turma tem início na próxima segunda-feira! As vagas são limitadas a 20 alunos por turma."

    # 4. Certificado e Reconhecimento
    if any(w in u_lower for w in ["certificado", "diploma", "reconhecido", "validade", "mec", "senai"]):
        return f"Sim! Ao concluir as 30 horas de capacitação e as práticas avaliativas, você recebe o certificado oficial de Aperfeiçoamento Profissional emitido pelo SENAI-SP, amplamente reconhecido no mercado em todo o Brasil. 📜"

    # 5. Pré-requisitos e Público-Alvo
    if any(w in u_lower for w in ["requisito", "quem pode", "precisa saber", "programar", "dificil", "difícil", "iniciante"]):
        return f"O curso foi desenhado para iniciantes na área de tecnologia e profissionais de negócios/gestão! Você só precisa ter conhecimentos básicos de informática e mais de 16 anos. Todas as ferramentas de IA são ensinadas do zero com foco prático."

    # 6. Intenção Positiva de Inscrição / Compra
    if any(w in u_lower for w in ["sim", "quero", "como faco", "como faço", "matricula", "matrícula", "inscrever", "fechar", "comprar", "gostei"]):
        return f"Excelente escolha! 🚀 Para reservarmos sua vaga na turma e enviarmos o link de matrícula segura, por favor me informe seu **Nome completo e WhatsApp com DDD**."

    # 7. Captura de Contato (Email / Telefone)
    if "@" in u_lower or any(char.isdigit() for char in u_lower):
        return f"Perfeito! Dados registrados com sucesso em nosso sistema de atendimento da {empresa}. 🎯 Um de nossos consultores educacionais entrará em contato via WhatsApp nas próximas horas para finalizar sua inscrição. Ficou com mais alguma dúvida?"

    # 8. Agradecimento e Despedida
    if any(w in u_lower for w in ["obrigado", "obrigada", "valeu", "tchau", "ate mais", "até mais", "show", "perfeito"]):
        return f"Foi um prazer ajudar! Conte sempre conosco na {empresa}. Se precisar de mais alguma informação, estou sempre por aqui. Tenha um excelente dia! ✨"

    # 9. Resposta Contextual Padrão
    return f"Entendi sua dúvida sobre '{user_input}'. Na {empresa}, nosso foco é capacitar você para aplicar inteligência artificial de forma prática e imediata. Gostaria que eu te explicasse a ementa detalhada das 30 horas de aula ou prefere falar sobre inscrições?"

def generate_copy_offline(produto: str, publico: str, objetivo: str, tom: str, framework: str) -> dict:
    """Gera copies completas e estruturadas usando templates heurísticos ricos."""
    if framework == "AIDA":
        return {
            "atencao": f"🚨 Descubra como revolucionar seus resultados em {produto}! Você ainda perde tempo com métodos tradicionais?",
            "interesse": f"Desenvolvido especificamente para {publico}, nossa solução une tecnologia de ponta e praticidade para atender seu foco em {objetivo.lower()}.",
            "desejo": f"Imagine alcançar seus objetivos com agilidade, sem frustração e com o dobro de eficiência comprovada pelo mercado.",
            "acao": f"👉 Clique no link agora e garanta uma demonstração exclusiva com condições especiais para {publico}!",
            "hashtags": f"#{produto.replace(' ', '')} #Inovação #MarketingDigital #{publico.split()[0]} #ResultadosReais"
        }
    else: # PAS
        return {
            "problema": f"❌ Você, que atua como {publico}, sabe como é exaustivo tentar atingir {objetivo.lower()} sem as ferramentas certas.",
            "agitacao": f"Cada dia adiando a mudança custa tempo, dinheiro e clientes que estão migrando para concorrentes mais ágeis.",
            "solucao": f"💡 Conheça {produto}: a resposta definitiva para automatizar processos, maximizar o retorno e colocar você na liderança.",
            "acao": f"🚀 Transforme sua realidade hoje mesmo. Toque no botão e comece sem compromisso!",
            "hashtags": f"#SolucaoInteligente #{produto.replace(' ', '')} #AltaPerformance #Estrategia"
        }

def analyze_ethics_offline(copy_text: str) -> dict:
    """Analisa conformidade ética, transparência e possíveis riscos legais/LGPD."""
    palavras_risco = ["garantido", "100%", "milagre", "fique rico", "sem esforço", "lucro certo", "dados pessoais", "vitalício grátis"]
    encontradas = [w for w in palavras_risco if w in copy_text.lower()]
    
    score = 100 - (len(encontradas) * 20)
    score = max(score, 30)
    
    alertas = []
    if encontradas:
        alertas.append(f"⚠️ Termos de alto risco ou promessas exageradas detectados: `{', '.join(encontradas)}`. No Brasil, o CONAR e o CDC proíbem promessas absolutas que não possam ser comprovadas.")
    else:
        alertas.append("✅ Nenhuma promessa exagerada explícita detectada.")
        
    alertas.append("✅ **Adequação à LGPD:** Se coletar leads (nome, e-mail, WhatsApp), certifique-se de incluir checkbox explícito de consentimento e link para a Política de Privacidade.")
    alertas.append("ℹ️ **Transparência de IA:** É uma boa prática informar aos usuários quando um atendimento ou conteúdo foi assistido por Inteligência Artificial.")
    
    return {
        "score": score,
        "nivel": "Excelente" if score >= 85 else "Atenção Necessária" if score >= 60 else "Alto Risco",
        "alertas": alertas
    }

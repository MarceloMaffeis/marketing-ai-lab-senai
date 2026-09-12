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
            help="Insira sua chave gratuita do Google AI Studio para respostas 100% dinâmicas em tempo real."
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
    Gera texto usando a API REST do Google Gemini (gemini-1.5-flash / gemini-2.0-flash).
    Corrige estritamente a ordenação de turnos (user -> model) exigida pela API.
    """
    api_key = get_api_key()
    
    if not api_key:
        return None

    # Modelos estáveis e rápidos do Gemini
    models_to_try = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
    
    # 1. Estruturação do histórico de conversa (Multi-turn)
    # A API do Gemini exige que o primeiro turno seja SEMPRE do usuário ('user')
    contents = []
    
    if chat_history:
        # Pula mensagens iniciais do bot para garantir que comece com 'user'
        started = False
        last_role = None
        
        for msg in chat_history:
            role = "user" if msg.get("role") == "user" else "model"
            
            # Só começa a adicionar a partir da primeira mensagem do usuário
            if not started and role == "user":
                started = True
                
            if started:
                # Evita mensagens repetidas do mesmo papel em sequência (ex: user seguido de user)
                if role != last_role:
                    contents.append({
                        "role": role,
                        "parts": [{"text": msg.get("content", "")}]
                    })
                    last_role = role
                else:
                    # Concatena se for do mesmo papel
                    if contents:
                        contents[-1]["parts"][0]["text"] += f"\n{msg.get('content', '')}"

    # Se a lista estiver vazia ou não terminar com o prompt atual
    if not contents or contents[-1]["role"] != "user":
        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })
    else:
        contents[-1]["parts"][0]["text"] = prompt

    # Montagem do Payload oficial
    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.75,
            "maxOutputTokens": 600,
            "topP": 0.95
        }
    }
    
    # Se houver instrução de sistema (Persona/FAQ)
    if system_instruction:
        payload["system_instruction"] = {
            "parts": [{"text": system_instruction}]
        }

    # Executa a requisição para os modelos
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        
        try:
            resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=12)
            
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"].strip()
            else:
                err = resp.json().get("error", {})
                err_msg = err.get("message", f"HTTP {resp.status_code}")
                # Exibe erro visível se for chave inválida
                if resp.status_code in [400, 403]:
                    # Tenta fallback sem system_instruction caso a versão não suporte
                    if "system_instruction" in payload:
                        payload_no_sys = payload.copy()
                        del payload_no_sys["system_instruction"]
                        # Prepend instrução no prompt
                        if contents:
                            contents[0]["parts"][0]["text"] = f"[Instrução do Sistema: {system_instruction}]\n\n{contents[0]['parts'][0]['text']}"
                        payload_no_sys["contents"] = contents
                        resp_retry = requests.post(url, json=payload_no_sys, headers={"Content-Type": "application/json"}, timeout=12)
                        if resp_retry.status_code == 200:
                            data = resp_retry.json()
                            candidates = data.get("candidates", [])
                            if candidates:
                                parts = candidates[0].get("content", {}).get("parts", [])
                                if parts and "text" in parts[0]:
                                    return parts[0]["text"].strip()
        except Exception:
            continue

    return None

def generate_chatbot_offline_reply(user_input: str, empresa: str, nome_bot: str, tom_bot: str, faq_conhecimento: str, history: list) -> str:
    """
    Motor heurístico avançado e humanizado que consulta o FAQ da empresa e responde de forma fluida.
    """
    u_lower = user_input.lower().strip()
    faq_lower = faq_conhecimento.lower() if faq_conhecimento else ""
    
    # 1. Busca inteligente no FAQ do usuário
    # Se o usuário perguntou sobre um curso ou assunto específico
    palavras_usuario = [p for p in u_lower.replace("?", "").replace("!", "").replace(",", "").split() if len(p) > 3]
    
    # Verifica se o termo está no FAQ
    termos_no_faq = [p for p in palavras_usuario if p in faq_lower]
    termos_nao_no_faq = [p for p in palavras_usuario if p not in ["voce", "você", "como", "onde", "qual", "quais", "tem", "existe", "sobre", "curso", "cursos", "escola", "aulas"] and p not in faq_lower]

    # Se perguntou algo específico que NÃO está no FAQ (Ex: "tem curso de CNC?")
    if any(p in u_lower for p in ["cnc", "solda", "mecanica", "mecânica", "eletrica", "elétrica", "administracao", "administração", "python", "culinaria"]) and not any(p in faq_lower for p in ["cnc", "solda", "mecanica", "eletrica"]):
        return f"No momento, aqui na **{empresa}**, os cursos com turmas abertas em destaque são os de **Marketing Digital com Inteligência Artificial** e **Automação Industrial**. Não temos turmas abertas para esse segmento específico no momento, mas posso registrar seu interesse! Deseja conhecer o conteúdo do curso de Marketing com IA?"

    # 2. Se perguntou sobre Marketing Digital ou IA (que está no FAQ)
    if any(w in u_lower for w in ["marketing", "inteligencia", "inteligência", "digital", "conteudo", "conteúdo", "grade", "ementa"]):
        return f"Sim! Temos o curso de **Marketing Digital com Inteligência Artificial (30 horas)** na {empresa}! Nele você aprende criação de conteúdos com IA, anúncios em redes sociais, mídia programática, análise de métricas e atendimento com chatbots. As aulas iniciam na próxima segunda-feira às 19h! Deseja que eu reserve uma vaga?"

    # 3. Preços e Valores
    if any(w in u_lower for w in ["preco", "preço", "valor", "custa", "investimento", "pagamento", "cartao", "cartão", "parcela", "desconto", "boleto"]):
        return f"O investimento do curso é de **R$ 490,00**, facilitado em até **10x sem juros** no cartão de crédito! 💳 Também temos desconto especial para pagamento à vista. Gostaria de garantir sua vaga?"

    # 4. Horários e Datas
    if any(w in u_lower for w in ["data", "quando", "inicio", "início", "horario", "horário", "dias", "turno", "noite"]):
        return f"As aulas acontecem no período noturno, das **19h às 22h**, na {empresa}. A próxima turma já começa na **próxima segunda-feira**. As vagas em laboratório são limitadas!"

    # 5. Certificado
    if any(w in u_lower for w in ["certificado", "diploma", "reconhecido", "validade"]):
        return f"Com certeza! Ao concluir as 30 horas práticas do curso, você recebe o **Certificado Oficial emitido pelo SENAI-SP**, com validade nacional e alto prestígio no mercado de trabalho. 📜"

    # 6. Saudações
    if any(u_lower.startswith(w) or u_lower == w for w in ["ola", "olá", "oi", "bom dia", "boa tarde", "boa noite", "opa"]):
        return f"Olá! Seja muito bem-vindo(a) à **{empresa}**! Sou a **{nome_bot}**. Como posso te ajudar hoje? Temos turmas abertas de Marketing Digital com IA e Automação!"

    # 7. Quero me inscrever / Fechar
    if any(w in u_lower for w in ["sim", "quero", "como faco", "como faço", "matricula", "matrícula", "inscrever", "fechar", "comprar"]):
        return f"Excelente decisão! 🚀 Para garantirmos sua vaga na turma da {empresa}, por favor me informe seu **Nome completo e WhatsApp com DDD**."

    # 8. Contato fornecido
    if "@" in u_lower or any(char.isdigit() for char in u_lower):
        return f"Perfeito! Seus dados foram recebidos com sucesso. 🎯 Nossa equipe pedagógica da **{empresa}** entrará em contato com você via WhatsApp ainda hoje para finalizar a inscrição. Muito obrigado!"

    # 9. Resposta fluida genérica
    return f"Entendido! Na **{empresa}**, estou à disposição para tirar todas as dúvidas sobre as turmas, horários, preços e conteúdo do curso de Marketing com Inteligência Artificial. O que mais gostaria de saber?"

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

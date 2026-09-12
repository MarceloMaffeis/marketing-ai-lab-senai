import os
import streamlit as st
import requests
import json

def get_api_key():
    """Recupera a chave de API de forma persistente entre abas e sessões."""
    # 1. Chave persistida no widget da barra lateral
    if "gemini_api_key_input" in st.session_state and st.session_state["gemini_api_key_input"]:
        return st.session_state["gemini_api_key_input"].strip()
    
    # 2. Chave na sessão
    if "user_gemini_key" in st.session_state and st.session_state["user_gemini_key"]:
        return st.session_state["user_gemini_key"].strip()
    
    # 3. Chave nos Secrets do Streamlit Cloud
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            return str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        pass
        
    return os.getenv("GEMINI_API_KEY", "")

def render_api_key_sidebar():
    """Renderiza o campo persistente na barra lateral."""
    with st.sidebar.expander("🔑 Configurar Chave de IA (Opcional)", expanded=False):
        current_key = get_api_key()
        
        st.text_input(
            "Google Gemini API Key:",
            type="password",
            placeholder="AIzaSy...",
            key="gemini_api_key_input",
            help="Cole sua chave gratuita do Google AI Studio para que o Chatbot e o estúdio usem IA em tempo real."
        )

        if current_key:
            st.caption("✅ Motor de IA Conectado: **Google Gemini Ativo**")
        else:
            st.caption("⚡ Motor Ativo: **Simulador Inteligente Integrado (Sem Custo)**")

def generate_text_ai(prompt: str, system_instruction: str = "", chat_history: list = None) -> str:
    """
    Gera texto dinâmico usando o Google Gemini REST API.
    Utiliza formato contextual consolidado à prova de falhas em qualquer versão de API.
    """
    api_key = get_api_key()
    
    if not api_key:
        return None

    # Modelos disponíveis na cota gratuita do Google AI Studio
    models_to_try = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
    
    # Constrói o histórico da conversa em formato de diálogo claro
    dialogo_formatado = ""
    if chat_history and len(chat_history) > 1:
        dialogo_formatado = "\n--- HISTÓRICO DA CONVERSA ANTERIOR ---\n"
        for msg in chat_history[:-1]:
            autor = "Cliente" if msg.get("role") == "user" else "Assistente"
            dialogo_formatado += f"{autor}: {msg.get('content', '')}\n"

    # Prompt Mestre enriquecido com a Persona e o Contexto
    prompt_completo = f"""Você deve agir estritamente de acordo com a seguinte Persona e Instruções:
{system_instruction}

{dialogo_formatado}
--- NOVA MENSAGEM DO CLIENTE ---
Cliente: {prompt}

Responda agora como a Persona, de forma extremamente humana, natural, cordial e contextualizada (sem clichês de robô):"""

    # Estrutura de Payload Universal (Compatível com 100% dos endpoints v1beta)
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt_completo}]
            }
        ],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 600,
            "topP": 0.95
        }
    }

    # Executa a chamada REST
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        
        try:
            resp = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=12
            )
            
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"].strip()
            else:
                # Se for erro com mensagem clara do Google
                err = resp.json().get("error", {})
                err_msg = err.get("message", f"HTTP {resp.status_code}")
                if resp.status_code in [400, 403]:
                    st.toast(f"⚠️ Google API: {err_msg}", icon="⚠️")
        except Exception as e:
            continue

    return None

def generate_chatbot_offline_reply(user_input: str, empresa: str, nome_bot: str, tom_bot: str, faq_conhecimento: str, history: list) -> str:
    """
    Motor heurístico humanizado de alta qualidade (utilizado se o aluno não tiver chave de API).
    """
    u_lower = user_input.lower().strip()
    faq_lower = faq_conhecimento.lower() if faq_conhecimento else ""
    
    # 1. Perguntas sobre quais cursos existem / opções
    if any(w in u_lower for w in ["quais cursos", "que cursos", "qual curso", "tem curso", "tem outros", "so tem", "só tem"]):
        if any(w in u_lower for w in ["so tem", "só tem", "apenas"]):
            return f"Além do curso de **Marketing Digital com IA**, nós também oferecemos turmas na área de **Automação Industrial** e capacitações corporativas aqui na **{empresa}**! 🎓 Você tem interesse em alguma área específica além do marketing?"
        return f"Aqui na **{empresa}**, nossas turmas principais abertas com inscrições abertas são:\n• **Marketing Digital com Inteligência Artificial (30h)**\n• **Automação Industrial**\n\nQual dessas áreas mais chama a sua atenção no momento?"

    # 2. Perguntas sobre dias da semana / horários ("Somente nas segundas?", "Que horas?")
    if any(w in u_lower for w in ["segundas", "dias", "quando", "horario", "horário", "noite", "semana"]):
        return f"As aulas começam na próxima segunda-feira e acontecem durante a semana no período noturno, das **19h às 22h**, totalizando 30 horas práticas de capacitação no laboratório da **{empresa}**. Esse horário encaixa na sua rotina?"

    # 3. Perguntas sobre cursos fora do FAQ (ex: CNC, solda, etc.)
    if any(p in u_lower for p in ["cnc", "solda", "mecanica", "mecânica", "eletrica", "elétrica", "administracao", "administração", "python"]):
        return f"No momento, aqui na **{empresa}**, as turmas com início imediato são as de **Marketing Digital com IA** e **Automação**. Não temos vagas abertas para esse curso específico nesta semana, mas posso anotar seu contato caso abra uma nova turma! Você gostaria de conhecer o curso de Marketing?"

    # 4. Preços e Valores
    if any(w in u_lower for w in ["preco", "preço", "valor", "custa", "investimento", "pagamento", "cartao", "cartão", "parcela", "desconto", "boleto"]):
        return f"O investimento do curso é de **R$ 490,00**, podendo ser parcelado em até **10x sem juros** no cartão de crédito! 💳 Para pagamento à vista no Pix, oferecemos condições especiais. Gostaria de garantir a sua vaga?"

    # 5. Certificado
    if any(w in u_lower for w in ["certificado", "diploma", "reconhecido", "validade"]):
        return f"Sim! Ao concluir as 30 horas do curso você recebe o **Certificado Oficial do SENAI-SP**, amplamente reconhecido pelas indústrias e empresas de todo o país. 📜"

    # 6. Saudações
    if any(u_lower.startswith(w) or u_lower == w for w in ["ola", "olá", "oi", "bom dia", "boa tarde", "boa noite", "opa"]):
        return f"Olá! Seja muito bem-vindo(a) à **{empresa}**! Sou a **{nome_bot}**. Como posso ajudar você hoje com as informações sobre nossas turmas e capacitações?"

    # 7. Quero me inscrever / Fechar
    if any(w in u_lower for w in ["sim", "quero", "como faco", "como faço", "matricula", "matrícula", "inscrever", "fechar", "comprar"]):
        return f"Excelente! 🚀 Para agilizarmos sua matrícula na turma da **{empresa}**, por favor digite seu **Nome completo e WhatsApp com DDD**."

    # 8. Contato fornecido
    if "@" in u_lower or any(char.isdigit() for char in u_lower):
        return f"Perfeito! Dados registrados com sucesso. 🎯 Nossa equipe de atendimento da **{empresa}** entrará em contato via WhatsApp para concluir sua matrícula. Muito obrigado!"

    # 9. Resposta fluida genérica
    return f"Com certeza! Aqui na **{empresa}**, nossa equipe está pronta para te apoiar. Você tem interesse em saber mais sobre o conteúdo programático, as datas de início ou as facilidades de pagamento?"

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

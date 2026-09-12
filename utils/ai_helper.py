import os
import streamlit as st
import requests
import json
import re

def get_api_key():
    """Recupera a chave de API de forma persistente."""
    if "gemini_api_key_input" in st.session_state and st.session_state["gemini_api_key_input"]:
        return st.session_state["gemini_api_key_input"].strip()
    
    if "user_gemini_key" in st.session_state and st.session_state["user_gemini_key"]:
        return st.session_state["user_gemini_key"].strip()
    
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            return str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        pass
        
    return os.getenv("GEMINI_API_KEY", "")

def render_api_key_sidebar():
    """Renderiza o campo de chave de API na barra lateral."""
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
    """
    api_key = get_api_key()
    
    if not api_key:
        return None

    models_to_try = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
    
    dialogo_formatado = ""
    if chat_history and len(chat_history) > 1:
        dialogo_formatado = "\n--- HISTÓRICO DA CONVERSA ANTERIOR ---\n"
        for msg in chat_history[:-1]:
            autor = "Cliente" if msg.get("role") == "user" else "Assistente"
            dialogo_formatado += f"{autor}: {msg.get('content', '')}\n"

    prompt_completo = f"""[DIRETRIZES DE PERSONA E REGRAS DE ATENDIMENTO]
{system_instruction}

{dialogo_formatado}
--- NOVA MENSAGEM DO CLIENTE ---
Cliente: {prompt}

Responda agora como a Persona, de forma extremamente humana, acolhedora, sensível ao sentimento do cliente (se ele recusar ou não quiser, respeite e trate a objeção; NUNCA force matrícula se ele disser que não quer):"""

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt_completo}]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 600,
            "topP": 0.95
        }
    }

    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        
        try:
            resp = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
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
                # Exibe aviso discreto se houver erro de cota ou chave inválida
                st.toast(f"⚠️ Gemini API ({model_name}): {err_msg}", icon="⚠️")
        except Exception:
            continue

    return None

def analyze_lead_scoring_advanced(messages: list) -> dict:
    """
    Analisa os sinais POSITIVOS e NEGATIVOS (Objeções/Recusas) do cliente
    para calcular o Lead Scoring real balanceado (Net Score).
    """
    user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
    if not user_msgs:
        return {
            "score": 10,
            "status": "Lead Frio",
            "pontos_positivos": 10,
            "penalidades": 0,
            "detalhes_positivos": ["Início de contato"],
            "detalhes_negativos": [],
            "classificacao": "❄️ Lead Frio (10/100)"
        }
        
    texto_completo = " ".join(user_msgs).lower()
    
    pontos_pos = 0
    pontos_neg = 0
    detalhes_pos = []
    detalhes_neg = []
    
    # 1. Análise de Engajamento
    if len(user_msgs) >= 1:
        pontos_pos += 10
        detalhes_pos.append(f"Engajamento inicial ({len(user_msgs)} msgs)")
    if len(user_msgs) >= 3:
        pontos_pos += 15
        detalhes_pos.append("Diálogo contínuo e ativo")
        
    # 2. DETECÇÃO DE SINAIS NEGATIVOS E RECUSAS (Subtrai pontos)
    padroes_recusa = [
        "não quero", "nao quero", "nenhum desses", "não tenho interesse", "nao tenho interesse",
        "nem pensar", "muito caro", "caro demais", "fora do orçamento", "não gostei", "nao gostei",
        "não posso", "nao posso", "horrível", "desisto", "sem interesse", "não serve", "nao serve"
    ]
    
    recusas_encontradas = [p for p in padroes_recusa if p in texto_completo]
    if recusas_encontradas:
        pontos_neg += 45
        detalhes_neg.append(f"Objeção/Recusa explícita: '{', '.join(recusas_encontradas)}'")
        
    if any(w in texto_completo for w in ["muito longe", "outra cidade", "horário ruim", "nao tenho tempo", "não tenho tempo"]):
        pontos_neg += 25
        detalhes_neg.append("Impedimento de logística ou horário")

    # 3. INTERESSE EM CONTEÚDO E HORÁRIOS (Apenas se não for recusa)
    if any(w in texto_completo for w in ["marketing", "inteligencia", "inteligência", "ia", "automação", "automacao", "grade", "ementa", "aprender", "horario", "horário", "quando"]):
        if not ("não quero" in texto_completo or "nenhum desses" in texto_completo):
            pontos_pos += 25
            detalhes_pos.append("Interesse no programa e grade do curso")
            
    # 4. SONDAGEM COMERCIAL (Preço, Pagamento)
    if any(w in texto_completo for w in ["preco", "preço", "valor", "custa", "quanto", "pagamento", "cartao", "cartão", "parcela", "desconto", "investimento", "pix"]):
        pontos_pos += 25
        detalhes_pos.append("Interesse financeiro e formas de pagamento")
        
    # 5. INTENÇÃO POSITIVA DE MATRÍCULA (Verifica que NÃO é precedido por 'não')
    # Regex para pegar "quero" apenas quando NÃO for "não quero"
    tem_quero_positivo = bool(re.search(r'(?<!não\s)(?<!nao\s)\b(quero|tenho interesse|gostaria|fazer matrícula|me inscrever)\b', texto_completo))
    tem_contato = "@" in texto_completo or any(char.isdigit() for char in texto_completo)
    
    if (tem_quero_positivo and not recusas_encontradas) or tem_contato:
        pontos_pos += 30
        detalhes_pos.append("Intenção de compra declarada / Contato informado")
        
    # Cálculo Final do Net Score (Equilíbrio entre Positivos e Penalidades)
    score_liquido = max(5, min(100, pontos_pos - pontos_neg))
    
    if pontos_neg >= 40:
        classificacao = f"⚠️ Objeção Ativa / Lead Desqualificado ({score_liquido}/100)"
        status = "Objeção Ativa"
    elif score_liquido >= 75:
        classificacao = f"🔥 Lead Quente / SQL ({score_liquido}/100): Alta intenção de compra!"
        status = "Lead Quente"
    elif score_liquido >= 40:
        classificacao = f"🌤️ Lead Morno / MQL ({score_liquido}/100): Em fase de pesquisa e qualificação."
        status = "Lead Morno"
    else:
        classificacao = f"❄️ Lead Frio ({score_liquido}/100): Contato inicial ou sem foco de compra."
        status = "Lead Frio"
        
    return {
        "score": score_liquido,
        "status": status,
        "pontos_positivos": pontos_pos,
        "penalidades": pontos_neg,
        "detalhes_positivos": detalhes_pos,
        "detalhes_negativos": detalhes_neg,
        "classificacao": classificacao
    }

def generate_chatbot_offline_reply(user_input: str, empresa: str, nome_bot: str, tom_bot: str, faq_conhecimento: str, history: list) -> str:
    """
    Motor heurístico avançado com tratamento inteligente de objeções e recusas.
    """
    u_lower = user_input.lower().strip()
    
    # 1. TRATAMENTO DE RECUSAS E DESINTERESSE ("Não quero nenhum desses", "não tenho interesse")
    if any(w in u_lower for w in ["não quero", "nao quero", "nenhum desses", "não tenho interesse", "nao tenho interesse", "nem pensar", "desisto", "não serve"]):
        return f"Entendo perfeitamente! 😊 Agradeço por me avisar. Que tipo de curso ou área profissional você está buscando no momento? Como o **SENAI** possui formações em diversas áreas industriais e de tecnologia, posso verificar se temos alguma outra opção futura que faça mais sentido para você!"

    # 2. Objeção de Preço ("Muito caro", "Não tenho dinheiro")
    if any(w in u_lower for w in ["muito caro", "caro demais", "nao tenho dinheiro", "não tenho dinheiro", "sem grana", "fora do orçamento"]):
        return f"Compreendo a sua preocupação com o orçamento. O curso de Marketing com IA pode ser parcelado em até **10x sem juros no cartão de crédito** ou com desconto especial no Pix. Além disso, temos programas de gratuidade e bolsas ao longo do ano na **{empresa}**. Gostaria que eu anotasse seu contato para avisar sobre novas bolsas?"

    # 3. Perguntas sobre quais cursos existem / opções
    if any(w in u_lower for w in ["quais cursos", "que cursos", "qual curso", "tem curso", "tem outros", "so tem", "só tem"]):
        if any(w in u_lower for w in ["so tem", "só tem", "apenas"]):
            return f"Além do curso de **Marketing Digital com IA (30h)**, nós também oferecemos turmas na área de **Automação Industrial** e programas corporativos sob demanda na **{empresa}**! Você teria interesse em alguma dessas áreas ou procura outro segmento?"
        return f"Aqui na **{empresa}**, nossas turmas em destaque no momento são:\n• **Marketing Digital com Inteligência Artificial (30h)**\n• **Automação Industrial**\n\nQual dessas áreas mais chama a sua atenção para a sua carreira?"

    # 4. Perguntas sobre dias da semana / horários ("Somente nas segundas?", "Que horas?")
    if any(w in u_lower for w in ["segundas", "dias", "quando", "horario", "horário", "noite", "semana"]):
        return f"As aulas iniciam na próxima segunda-feira e acontecem durante a semana no período noturno, das **19h às 22h**, no laboratório da **{empresa}**. Esse formato noturno fica acessível para a sua rotina?"

    # 5. Cursos fora do FAQ (ex: CNC, solda, etc.)
    if any(p in u_lower for p in ["cnc", "solda", "mecanica", "mecânica", "eletrica", "elétrica", "administracao", "administração", "python"]):
        return f"No momento, aqui na **{empresa}**, as turmas abertas para matrícula imediata são as de **Marketing com IA** e **Automação**. Não temos turmas abertas para esse curso específico nesta semana, mas posso anotar seu contato caso abra uma turma futura! Gostaria de saber mais sobre as opções disponíveis?"

    # 6. Preços e Valores
    if any(w in u_lower for w in ["preco", "preço", "valor", "custa", "investimento", "pagamento", "cartao", "cartão", "parcela", "desconto", "boleto"]):
        return f"O investimento do curso é de **R$ 490,00**, facilitado em até **10x sem juros** no cartão de crédito! 💳 Também oferecemos desconto especial para pagamento à vista. Gostaria de garantir a sua vaga na turma?"

    # 7. Certificado
    if any(w in u_lower for w in ["certificado", "diploma", "reconhecido", "validade"]):
        return f"Sim! Ao concluir as 30 horas práticas do curso você recebe o **Certificado Oficial do SENAI-SP**, com validade em todo o território nacional e alto reconhecimento na indústria. 📜"

    # 8. Saudações
    if any(u_lower.startswith(w) or u_lower == w for w in ["ola", "olá", "oi", "bom dia", "boa tarde", "boa noite", "opa"]):
        return f"Olá! Seja muito bem-vindo(a) à **{empresa}**! Sou a **{nome_bot}**. Como posso ajudar você hoje com as informações sobre nossos cursos e turmas?"

    # 9. Intenção declarada de Matrícula (Sem negações)
    if any(w in u_lower for w in ["quero me inscrever", "quero fazer", "como faco a matricula", "como faço a matrícula", "tenho interesse"]):
        return f"Excelente escolha! 🚀 Para agilizarmos sua reserva de vaga na turma da **{empresa}**, por favor me informe seu **Nome completo e WhatsApp com DDD**."

    # 10. Contato fornecido
    if "@" in u_lower or any(char.isdigit() for char in u_lower):
        return f"Perfeito! Dados registrados com sucesso em nosso sistema de atendimento da **{empresa}**. 🎯 Nossa equipe entrará em contato via WhatsApp para concluir sua inscrição. Muito obrigado!"

    # 11. Resposta fluida contextual
    return f"Entendido! Na **{empresa}**, estou à disposição para te explicar qualquer detalhe sobre os conteúdos, dias de aula, valores ou formas de pagamento. O que mais você gostaria de saber?"

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

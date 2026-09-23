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

    models_to_try = [
        "gemini-flash-latest",
        "gemini-flash-lite-latest",
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-2.5-flash",
        "gemini-1.5-flash"
    ]
    
    if chat_history is not None:
        dialogo_formatado = ""
        if len(chat_history) > 1:
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
    else:
        instrucao_bloco = f"[DIRETRIZES DO ESPECIALISTA SENAI]\n{system_instruction}\n\n" if system_instruction else ""
        prompt_completo = f"{instrucao_bloco}{prompt}"

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt_completo}]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 800,
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
                timeout=12
            )
            
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"].strip()
        except Exception:
            continue

    return None

def analyze_lead_scoring_advanced(messages: list) -> dict:
    """
    Analisa os sinais POSITIVOS e NEGATIVOS (Objeções/Recusas) do cliente
    para calcular o Lead Scoring real balanceado (Net Score), aplicável a qualquer negócio.
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
        detalhes_pos.append(f"Engajamento inicial ({len(user_msgs)} mensagens trocadas)")
    if len(user_msgs) >= 3:
        pontos_pos += 15
        detalhes_pos.append("Diálogo contínuo e ativo no atendimento")
        
    # 2. DETECÇÃO DE RECUSAS E BARREIRAS (Subtrai pontos)
    padroes_recusa = [
        "não quero", "nao quero", "nenhum desses", "nenhum desse", "não tenho interesse", "nao tenho interesse",
        "nem pensar", "muito caro", "caro demais", "fora do orçamento", "fora do orcamento", "não gostei", "nao gostei",
        "não posso", "nao posso", "horrível", "desisto", "sem interesse", "não serve", "nao serve"
    ]
    
    recusas_encontradas = [p for p in padroes_recusa if p in texto_completo]
    if recusas_encontradas:
        pontos_neg += 45
        detalhes_neg.append(f"Objeção/Recusa explícita: '{', '.join(set(recusas_encontradas))}'")
        
    if any(w in texto_completo for w in ["muito longe", "outra cidade", "horário ruim", "horario ruim", "demora muito", "prazo longo", "nao tenho tempo", "não tenho tempo"]):
        pontos_neg += 25
        detalhes_neg.append("Impedimento de logística, distância ou prazo")

    # 3. INTERESSE EM PRODUTOS / SERVIÇOS / SOLUÇÕES / CATÁLOGO
    termos_interesse = [
        "produto", "servico", "serviço", "catalogo", "catálogo", "cardapio", "cardápio", "modelo", "tamanho",
        "opcao", "opção", "opcoes", "opções", "grade", "ementa", "curso", "plano", "imovel", "imóvel", "consulta",
        "como funciona", "detalhes", "funciona", "especificacao", "especificação", "aprender"
    ]
    if any(w in texto_completo for w in termos_interesse) and not recusas_encontradas:
        pontos_pos += 25
        detalhes_pos.append("Interesse ativo no catálogo de produtos, serviços ou soluções")
            
    # 4. SONDAGEM COMERCIAL (Preço, Pagamento, Investimento)
    termos_preco = [
        "preco", "preço", "valor", "custa", "quanto", "pagamento", "cartao", "cartão", "parcela",
        "desconto", "investimento", "pix", "taxa", "mensalidade", "a vista", "à vista", "condicoes", "condições"
    ]
    if any(w in texto_completo for w in termos_preco):
        pontos_pos += 25
        detalhes_pos.append("Sondagem comercial: Consulta de valores e formas de pagamento")
        
    # 5. CONSULTA DE LOGÍSTICA / AGENDAMENTO / HORÁRIOS / DISPONIBILIDADE
    termos_agenda = [
        "horario", "horário", "quando", "dias", "dia", "endereco", "endereço", "onde fica", "localizacao",
        "localização", "entrega", "frete", "prazo", "agendar", "agenda", "vaga", "disponivel", "disponível"
    ]
    if any(w in texto_completo for w in termos_agenda) and not recusas_encontradas:
        pontos_pos += 15
        detalhes_pos.append("Consulta de disponibilidade, horários, prazos ou logística")
        
    # 6. INTENÇÃO DE COMPRA / AGENDAMENTO / FECHAMENTO (Sem recusas prévias)
    padroes_conversao = [
        "quero comprar", "quero agendar", "quero fechar", "quero contratar", "quero fazer", "tenho interesse",
        "vou querer", "como faco o pedido", "como faço o pedido", "fazer reserva", "fazer matricula", "fazer matrícula",
        "me inscrever", "quero esse", "quero um", "comprar agora", "fechar pedido", "garantir"
    ]
    tem_conversao = any(p in texto_completo for p in padroes_conversao)
    tem_contato = "@" in texto_completo or any(char.isdigit() for char in texto_completo)
    
    if (tem_conversao and not recusas_encontradas) or tem_contato:
        pontos_pos += 30
        detalhes_pos.append("Alta intenção de conversão / Dados de contato fornecidos")
        
    # Cálculo Final do Net Score (Equilíbrio entre Positivos e Penalidades)
    score_liquido = max(5, min(100, pontos_pos - pontos_neg))
    
    if pontos_neg >= 40:
        classificacao = f"⚠️ Objeção Ativa / Lead em Risco ({score_liquido}/100): Necessita contorno de objeção."
        status = "Objeção Ativa"
    elif score_liquido >= 75:
        classificacao = f"🔥 Lead Quente / SQL ({score_liquido}/100): Alta prontidão de compra/agendamento!"
        status = "Lead Quente"
    elif score_liquido >= 40:
        classificacao = f"🌤️ Lead Morno / MQL ({score_liquido}/100): Em fase de pesquisa e qualificação."
        status = "Lead Morno"
    else:
        classificacao = f"❄️ Lead Frio ({score_liquido}/100): Contato inicial ou sem intenção declarada."
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

def generate_chatbot_offline_reply(
    user_input: str,
    empresa: str,
    nome_bot: str,
    tom_bot: str,
    faq_conhecimento: str,
    history: list = None,
    papel_bot: str = "Consultor(a) de Atendimento",
    segmento: str = "Geral"
) -> str:
    """
    Motor RAG heurístico avançado com interpretação dinâmica da Base de Conhecimento,
    adaptação universal para qualquer nicho de negócio, persona e tratamento de objeções.
    """
    u_lower = user_input.lower().strip()
    
    # Extrai e limpa as linhas da Base de Conhecimento (RAG)
    faq_lines = [line.strip().lstrip("•-*0123456789. ") for line in faq_conhecimento.split("\n") if line.strip()]
    
    # 1. TRATAMENTO DE RECUSAS E DESINTERESSE ("Não quero", "não tenho interesse", etc.)
    padroes_recusa = [
        "não quero", "nao quero", "nenhum desses", "nenhum desse", "não tenho interesse", "nao tenho interesse",
        "nem pensar", "desisto", "não serve", "nao serve", "não gostei", "nao gostei", "não posso", "nao posso"
    ]
    if any(w in u_lower for w in padroes_recusa):
        if "Vendedor" in tom_bot:
            return f"Entendido! Compreendo perfeitamente. Posso registrar seu contato para avisar com prioridade quando tivermos novas opções, lançamentos ou condições promocionais na **{empresa}**?"
        elif "Técnico" in tom_bot:
            return f"Atendimento atualizado: registro finalizado sem interesse neste momento. Na **{empresa}**, novos itens e especificações são atualizados periodicamente. À disposição."
        elif "Descontraído" in tom_bot:
            return f"Tudo bem, sem problemas! 😉 Se mudar de ideia ou quiser tirar qualquer outra dúvida na **{empresa}**, é só me chamar por aqui. Tenha um ótimo dia!"
        elif "Luxo" in tom_bot:
            return f"Agradecemos pela sua atenção. Na **{empresa}**, permanecemos à sua inteira disposição para quando desejar uma experiência exclusiva."
        else: # Consultivo / Empático
            return f"Entendo perfeitamente! 😊 Agradeço por me avisar. Que tipo de produto, serviço ou solução você está buscando no momento? Na **{empresa}**, posso te orientar caso tenhamos novidades futuras alinhadas à sua necessidade!"

    # 2. Objeção de Preço ("Muito caro", "Não tenho dinheiro")
    if any(w in u_lower for w in ["muito caro", "caro demais", "nao tenho dinheiro", "não tenho dinheiro", "sem grana", "fora do orçamento", "fora do orcamento"]):
        linhas_preco = [l for l in faq_lines if any(k in l.lower() for k in ["r$", "investimento", "preço", "preco", "pagamento", "cartão", "cartao", "parcela", "sem juros", "pix", "grátis", "gratuito", "desconto", "taxa"])]
        info_preco = ("\n• " + "\n• ".join(linhas_preco)) if linhas_preco else "\nTemos opções de parcelamento facilitado e condições flexíveis de pagamento."
        return f"Compreendo a sua preocupação com o orçamento! Na **{empresa}**, buscamos sempre facilitar as condições:{info_preco}\n\nGostaria que eu verificasse uma condição personalizada ou opção de entrada mais acessível para você?"

    # 3. Perguntas sobre Catálogo / Opções / O que oferecem / Cardápio / Serviços
    termos_catalogo = ["quais produtos", "quais servicos", "quais serviços", "quais cursos", "que produtos", "que servicos", "que serviços", "o que tem", "o que voces tem", "o que vocês têm", "catalogo", "catálogo", "cardapio", "cardápio", "opcoes", "opções", "quais sao", "quais são", "tem opcao", "tem opção", "trabalham com"]
    if any(w in u_lower for w in termos_catalogo) or u_lower in ["produtos", "serviços", "servicos", "cursos", "cardapio", "cardápio", "opcoes"]:
        if faq_lines:
            faq_resumo = "\n".join([f"• **{line}**" for line in faq_lines])
            cta = "Qual dessas opções podemos reservar ou preparar para você hoje?" if "Vendedor" in tom_bot else "Qual dessas opções melhor atende o que você está procurando?"
            return f"Aqui na **{empresa}**, nossas principais opções e informações disponíveis são:\n\n{faq_resumo}\n\n{cta}"
        else:
            return f"Aqui na **{empresa}**, oferecemos soluções sob medida! Como posso te direcionar para a opção desejada?"

    # 4. Perguntas sobre Horários / Datas / Prazos / Início / Endereço / Localização / Frete
    if any(w in u_lower for w in ["horario", "horário", "quando", "dias", "dia", "noite", "semana", "inicio", "início", "comeca", "começa", "horas", "prazo", "entrega", "frete", "onde fica", "endereco", "endereço", "localizacao", "localização", "turno"]):
        linhas_horario = [l for l in faq_lines if any(k in l.lower() for k in ["início", "inicio", "horário", "horario", "hs", "horas", "segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo", "noite", "manhã", "tarde", "entrega", "prazo", "frete", "endereço", "endereco", "rua", "av", "local", "sedex", "pac"])]
        if linhas_horario:
            info_h = "\n• " + "\n• ".join(linhas_horario)
            return f"Sobre horários, prazos e localização na **{empresa}**:\n{info_h}\n\nEssas condições atendem à sua necessidade?"
        else:
            return f"Na **{empresa}**, contamos com horários e prazos flexíveis de atendimento. Gostaria de confirmar a disponibilidade para algum dia ou turno específico?"

    # 5. Preços e Valores / Formas de Pagamento
    if any(w in u_lower for w in ["preco", "preço", "valor", "custa", "investimento", "pagamento", "cartao", "cartão", "parcela", "desconto", "pix", "boleto", "mensalidade", "quanto custa"]):
        linhas_preco = [l for l in faq_lines if any(k in l.lower() for k in ["r$", "investimento", "preço", "preco", "valor", "cartão", "cartao", "parcela", "juros", "pix", "grátis", "gratuito", "desconto", "taxa", "mensalidade"])]
        if linhas_preco:
            info_p = "\n• " + "\n• ".join(linhas_preco)
            return f"Em relação a valores e pagamento na **{empresa}**:\n{info_p}\n\nPodemos dar andamento no seu pedido ou agendamento?"
        else:
            return f"Os valores e condições na **{empresa}** contam com opções facilitadas. Gostaria de receber uma proposta detalhada?"

    # 6. Garantia / Certificado / Política de Troca / Requisitos
    if any(w in u_lower for w in ["garantia", "troca", "devolucao", "devolução", "certificado", "diploma", "requisito", "requisitos", "qualidade"]):
        linhas_garantia = [l for l in faq_lines if any(k in l.lower() for k in ["garantia", "troca", "certificado", "diploma", "requisito", "oficial", "validade", "conclusão"])]
        if linhas_garantia:
            return f"Sim! Na **{empresa}**: {linhas_garantia[0]} ✨"
        return f"Com certeza! Na **{empresa}**, garantimos total qualidade, procedência e suporte em todos os nossos atendimentos."

    # 7. Saudações
    if any(u_lower.startswith(w) or u_lower == w for w in ["ola", "olá", "oi", "bom dia", "boa tarde", "boa noite", "opa", "tudo bem", "e ai", "e aí"]):
        return f"Olá! Seja muito bem-vindo(a) à **{empresa}**! Sou {nome_bot}, {papel_bot.lower()}. Como posso te ajudar hoje com nossos produtos e serviços?"

    # 8. Intenção declarada de Compra / Agendamento / Contratação (Sem recusas)
    padroes_compra = ["quero comprar", "quero agendar", "quero fechar", "como faco o pedido", "como faço o pedido", "fazer reserva", "quero me inscrever", "quero fazer", "tenho interesse", "fazer pedido", "quero contratar", "quero"]
    if any(w in u_lower for w in padroes_compra) and not any(r in u_lower for r in padroes_recusa):
        return f"Excelente escolha! 🚀 Para agilizarmos seu atendimento e reserva na **{empresa}**, por favor me informe seu **Nome completo e WhatsApp com DDD**."

    # 9. Contato fornecido (WhatsApp, E-mail, Telefone)
    if "@" in u_lower or any(char.isdigit() for char in u_lower):
        return f"Perfeito! Dados registrados com sucesso em nosso sistema da **{empresa}**. 🎯 Nossa equipe entrará em contato via WhatsApp para confirmar os detalhes. Muito obrigado pela preferência!"

    # 10. Busca Semântica Contextual nas Linhas da Base de Conhecimento (RAG)
    palavras_chave = [w for w in re.findall(r'\w+', u_lower) if len(w) >= 3 and w not in ["sobre", "para", "como", "voces", "vocês", "estou", "quero", "saber", "qual", "quais", "onde", "quando", "tem", "uma", "esse", "essa"]]
    linhas_match = []
    for line in faq_lines:
        if any(kw in line.lower() for kw in palavras_chave):
            linhas_match.append(line)
            
    if linhas_match:
        res_match = "\n• " + "\n• ".join(linhas_match)
        return f"Encontrei as seguintes informações sobre isso na base da **{empresa}**:\n{res_match}\n\nFicou alguma dúvida ou gostaria de avançar?"

    # 11. Resposta fluida contextual
    return f"Entendido! Na **{empresa}**, estou à disposição para te explicar qualquer detalhe sobre produtos, serviços, valores, prazos ou formas de pagamento. Como posso te auxiliar?"

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

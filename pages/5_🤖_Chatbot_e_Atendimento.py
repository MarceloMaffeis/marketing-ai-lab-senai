import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from utils.auth import check_authentication
from utils.ai_helper import render_api_key_sidebar, generate_text_ai, generate_chatbot_offline_reply, get_api_key
from utils.export_helper import generate_html_report, render_download_button
from utils.ui_components import render_sidebar_header, render_sidebar_footer, render_academic_footer

st.set_page_config(page_title="Chatbot & Automação | SENAI", page_icon="🤖", layout="wide")
render_sidebar_header()
check_authentication()
render_api_key_sidebar()

st.title("🤖 Construtor de Chatbot & Qualificação de Leads")
st.caption("Alinhado ao **Módulo 1 da Ementa SENAI**: Automação de marketing, chatbots de atendimento, assistentes virtuais e qualificação de clientes.")

# Inicialização do histórico do chat na sessão
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {"role": "assistant", "content": "Olá! 👋 Sou o assistente virtual da instituição. Como posso ajudar você hoje?"}
    ]

col_config, col_chat = st.columns([1, 2], gap="large")

with col_config:
    st.subheader("⚙️ 1. Configurar Assistente")
    nome_bot = st.text_input("Nome do Assistente:", value="Sofia", placeholder="Ex: Lucas, Sofia, Ana...")
    empresa = st.text_input("Nome da Empresa / Escola:", value="Escola SENAI Sorocaba", placeholder="Ex: Tech Store, Barbearia Silva...")
    
    tom_bot = st.selectbox(
        "Tom de Voz do Atendimento:",
        ["Consultivo & Empático (Especialista)", "Vendedor Direto & Focado em Fechamento", "Técnico & Preciso", "Descontraído & Amigável"]
    )
    
    faq_conhecimento = st.text_area(
        "Base de Conhecimento / FAQ da Empresa:",
        value="• Cursos disponíveis: Marketing Digital com IA (30h) e Automação Industrial.\n• Investimento: R$ 490,00 ou 10x sem juros no cartão.\n• Início das aulas: Próxima segunda-feira às 19h.\n• Certificado oficial emitido ao final.",
        height=120
    )
    
    st.markdown("---")
    st.subheader("🎯 2. Termômetro de Lead Scoring (IA)")
    
    # -------------------------------------------------------------
    # CÁLCULO DINÂMICO DE LEAD SCORING DIDÁTICO (PADRÃO HUBSPOT / RD STATION)
    # -------------------------------------------------------------
    user_msgs = [m["content"] for m in st.session_state["chat_messages"] if m["role"] == "user"]
    historico_texto = " ".join(user_msgs).lower()
    
    # Critérios de pontuação
    pontos_engajamento = 0
    pontos_interesse = 0
    pontos_comercial = 0
    pontos_conversao = 0
    
    # 1. Engajamento pela profundidade da conversa
    if len(user_msgs) >= 1:
        pontos_engajamento += 15
    if len(user_msgs) >= 3:
        pontos_engajamento += 15
        
    # 2. Interesse em Conteúdo, Grade e Horários
    if any(w in historico_texto for w in ["curso", "cursos", "marketing", "ia", "automacao", "automação", "grade", "ementa", "aprender", "horario", "horário", "segunda", "noite", "aulas", "quando"]):
        pontos_interesse = 25
        
    # 3. Interesse Comercial / Valores / Pagamento
    if any(w in historico_texto for w in ["preco", "preço", "valor", "custa", "quanto", "pagamento", "cartao", "cartão", "parcela", "desconto", "investimento", "pix"]):
        pontos_comercial = 25
        
    # 4. Intenção de Fechamento / Envio de Dados de Contato
    if any(w in historico_texto for w in ["sim", "quero", "matricula", "matrícula", "inscrever", "fechar", "comprar", "vaga"]) or "@" in historico_texto or any(char.isdigit() for char in historico_texto):
        pontos_conversao = 25
        
    score_total = min(100, pontos_engajamento + pontos_interesse + pontos_comercial + pontos_conversao)
    
    # Exibição da Barra de Progresso do Lead Scoring
    st.progress(score_total / 100)
    
    if score_total >= 75:
        st.success(f"🔥 **Lead Quente / SQL ({score_total}/100)**: Alta intenção de matrícula! Encaminhar imediatamente para um consultor humano.")
    elif score_total >= 40:
        st.warning(f"🌤️ **Lead Morno / MQL ({score_total}/100)**: Cliente engajado pesquisando horários, conteúdo e valores.")
    else:
        st.info(f"❄️ **Lead Frio ({score_total}/100)**: Primeiro contato ou pesquisa inicial de curiosidade.")
        
    with st.expander("📊 Critérios de Pontuação Ativos"):
        st.write(f"• **Engajamento na Conversa:** {'✅ +' if pontos_engajamento > 0 else '⏳ '}{pontos_engajamento} pts ({len(user_msgs)} msgs)")
        st.write(f"• **Interesse em Cursos & Horários:** {'✅ +' if pontos_interesse > 0 else '⏳ '}{pontos_interesse} pts")
        st.write(f"• **Sondagem de Preço & Pagamento:** {'✅ +' if pontos_comercial > 0 else '⏳ '}{pontos_comercial} pts")
        st.write(f"• **Intenção de Matrícula & Contato:** {'✅ +' if pontos_conversao > 0 else '⏳ '}{pontos_conversao} pts")
        
    if st.button("🧹 Limpar e Reiniciar Chat", use_container_width=True):
        st.session_state["chat_messages"] = [
            {"role": "assistant", "content": f"Olá! 👋 Sou {nome_bot}, assistente virtual da {empresa}. Como posso te ajudar hoje?"}
        ]
        st.rerun()

with col_chat:
    status_ia = "🟢 Conectado ao Google Gemini" if get_api_key() else "⚡ Modo Inteligente Offline"
    st.subheader(f"💬 Simulador de Atendimento ao Vivo • {nome_bot}")
    st.caption(f"Status da IA: **{status_ia}** | Empresa: **{empresa}**")
    
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    user_input = st.chat_input("Digite sua mensagem para testar o assistente...")
    
    if user_input:
        st.session_state["chat_messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
            
        with st.chat_message("assistant"):
            with st.spinner(f"{nome_bot} está digitando..."):
                system_instruction = f"""
                Você é {nome_bot}, consultor(a) e atendente de relacionamento da {empresa}.
                Você atende clientes de forma 100% humanizada, empática, inteligente e conversacional (sem respostas prontas ou robóticas).
                
                Instruções de Comportamento:
                1. Tom de voz: {tom_bot}.
                2. Use o FAQ abaixo como base de conhecimento real:
                {faq_conhecimento}
                3. Responda diretamente ao que o cliente acabou de perguntar de forma clara e objetiva (máximo 2 a 3 frases).
                4. Se o cliente perguntar sobre cursos fora do FAQ (ex: CNC, solda, etc.), informe com simpatia que no momento as turmas abertas são as do FAQ e ofereça o conteúdo disponível.
                5. Se o cliente perguntar de dias, horários ou valores, use exatamente os dados do FAQ com entusiasmo.
                6. Quando o cliente demonstrar intenção positiva, convide-o a enviar o Nome e WhatsApp para formalizar a reserva.
                """
                
                resposta = generate_text_ai(
                    prompt=user_input,
                    system_instruction=system_instruction,
                    chat_history=st.session_state["chat_messages"]
                )
                
                if not resposta:
                    resposta = generate_chatbot_offline_reply(
                        user_input=user_input,
                        empresa=empresa,
                        nome_bot=nome_bot,
                        tom_bot=tom_bot,
                        faq_conhecimento=faq_conhecimento,
                        history=st.session_state["chat_messages"]
                    )

                st.write(resposta)
                st.session_state["chat_messages"].append({"role": "assistant", "content": resposta})
                st.rerun()

    st.markdown("---")
    st.subheader("📥 Exportar Transcrição do Atendimento")
    
    transcricao_html = "<div style='font-family: monospace;'>"
    for m in st.session_state["chat_messages"]:
        autor = f"<strong>{nome_bot} (IA):</strong>" if m["role"] == "assistant" else "<strong>Cliente:</strong>"
        transcricao_html += f"<p>{autor} {m['content']}</p>"
    transcricao_html += "</div>"
    
    lead_status_nome = 'Lead Quente (SQL)' if score_total >= 75 else 'Lead Morno (MQL)' if score_total >= 40 else 'Lead Frio'
    
    secoes_chat = [
        ("1. Perfil do Assistente Configurado", f"<p><strong>Nome:</strong> {nome_bot}<br><strong>Empresa:</strong> {empresa}<br><strong>Tom de Voz:</strong> {tom_bot}</p>"),
        ("2. Transcrição Completa da Conversa", transcricao_html),
        ("3. Avaliação de Qualificação de Lead (Lead Scoring)", f"<p><strong>Pontuação Final:</strong> {score_total}/100 ({lead_status_nome})</p><ul><li>Engajamento: {pontos_engajamento} pts</li><li>Interesse em Conteúdo: {pontos_interesse} pts</li><li>Sondagem de Valores: {pontos_comercial} pts</li><li>Intenção de Matrícula: {pontos_conversao} pts</li></ul>")
    ]
    
    html_chat = generate_html_report(
        title=f"Relatório de Atendimento & Lead Scoring: {nome_bot}",
        subtitle=f"Automação de Conversação para {empresa}",
        sections=secoes_chat
    )
    
    render_download_button(
        label="📥 Baixar Transcrição e Diagnóstico de Lead em HTML",
        data=html_chat,
        file_name=f"transcricao_chatbot_{nome_bot.lower()}.html",
        mime="text/html"
    )

render_sidebar_footer()
render_academic_footer()

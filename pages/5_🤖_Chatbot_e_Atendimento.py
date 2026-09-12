import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from utils.auth import check_authentication
from utils.ai_helper import render_api_key_sidebar, generate_text_ai, generate_chatbot_offline_reply, get_api_key, analyze_lead_scoring_advanced
from utils.export_helper import generate_html_report, render_download_button
from utils.ui_components import render_sidebar_header, render_sidebar_footer, render_academic_footer

st.set_page_config(page_title="Chatbot & Automação | SENAI", page_icon="🤖", layout="wide")
render_sidebar_header()
check_authentication()
render_api_key_sidebar()

st.title("🤖 Construtor de Chatbot & Qualificação de Leads")
st.caption("Alinhado ao **Módulo 1 da Ementa SENAI**: Automação de marketing, chatbots de atendimento, assistentes virtuais, tratamento de objeções e qualificação de clientes.")

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
    # ANÁLISE AVANÇADA DE SINAIS POSITIVOS E NEGATIVOS
    # -------------------------------------------------------------
    analise_scoring = analyze_lead_scoring_advanced(st.session_state["chat_messages"])
    score_val = analise_scoring["score"]
    
    # Barra de Progresso Visual
    st.progress(score_val / 100)
    
    if analise_scoring["status"] == "Objeção Ativa":
        st.error(analise_scoring["classificacao"])
    elif analise_scoring["status"] == "Lead Quente":
        st.success(analise_scoring["classificacao"])
    elif analise_scoring["status"] == "Lead Morno":
        st.warning(analise_scoring["classificacao"])
    else:
        st.info(analise_scoring["classificacao"])
        
    with st.expander("📊 Detalhamento dos Sinais (Positivos vs. Objeções)", expanded=True):
        st.markdown(f"**Pontos Positivos (+{analise_scoring['pontos_positivos']} pts):**")
        for dp in analise_scoring["detalhes_positivos"]:
            st.write(f"• ✅ {dp}")
            
        if analise_scoring["penalidades"] > 0:
            st.markdown(f"**Penalidades / Objeções (-{analise_scoring['penalidades']} pts):**")
            for dn in analise_scoring["detalhes_negativos"]:
                st.write(f"• ❌ {dn}")
        else:
            st.caption("Nenhuma objeção ou recusa detectada até o momento.")
            
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
                Você atende clientes de forma 100% humanizada, empática, inteligente e conversacional.
                
                Instruções de Comportamento e Tratamento de Objeções:
                1. Tom de voz: {tom_bot}.
                2. Base de Informações da Empresa (FAQ):
                {faq_conhecimento}
                3. SE O CLIENTE REJEITAR, DISSER 'NÃO QUERO', 'NÃO TENHO INTERESSE' OU RECLAMAR:
                   - NUNCA comemore e NUNCA peça dados de matrícula!
                   - Seja educado, acolhedor, compreensivo e pergunte se ele procura alguma outra área no SENAI.
                4. SE O CLIENTE PERGUNTAR DE CURSOS FORA DO FAQ (ex: CNC, solda, etc.):
                   - Explique que as turmas abertas hoje são as do FAQ e ofereça detalhes se ele quiser.
                5. SE O CLIENTE DEMONSTRAR INTERESSE REAL (preço, datas, matrícula):
                   - Explique com clareza e entusiasmo, convidando a enviar o Nome e WhatsApp.
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
    
    secoes_chat = [
        ("1. Perfil do Assistente Configurado", f"<p><strong>Nome:</strong> {nome_bot}<br><strong>Empresa:</strong> {empresa}<br><strong>Tom de Voz:</strong> {tom_bot}</p>"),
        ("2. Transcrição Completa da Conversa", transcricao_html),
        ("3. Avaliação de Qualificação de Lead (Lead Scoring)", f"<p><strong>Status:</strong> {analise_scoring['classificacao']}<br><strong>Pontos Positivos:</strong> +{analise_scoring['pontos_positivos']} pts<br><strong>Penalidades/Objeções:</strong> -{analise_scoring['penalidades']} pts</p>")
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

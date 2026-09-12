import streamlit as st
from utils.auth import check_authentication
from utils.ai_helper import render_api_key_sidebar, generate_text_ai, generate_chatbot_offline_reply
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
        {"role": "assistant", "content": "Olá! 👋 Sou o assistente virtual inteligente da empresa. Como posso ajudar você hoje?"}
    ]

col_config, col_chat = st.columns([1, 2], gap="large")

with col_config:
    st.subheader("⚙️ 1. Configurar Assistente")
    nome_bot = st.text_input("Nome do Assistente:", value="Sofia", placeholder="Ex: Lucas, Sofia, Ana...")
    empresa = st.text_input("Nome da Empresa / Escola:", value="Escola SENAI de Tecnologia", placeholder="Ex: Tech Store, Barbearia Silva...")
    
    tom_bot = st.selectbox(
        "Tom de Voz do Atendimento:",
        ["Consultivo & Empático (Especialista)", "Vendedor Direto & Focado em Fechamento", "Técnico & Preciso", "Descontraído & Amigável"]
    )
    
    faq_conhecimento = st.text_area(
        "Base de Conhecimento / FAQ da Empresa:",
        value="• Cursos disponíveis: Marketing Digital com IA (30h) e Automação Industrial.\n• Investimento: R$ 490,00 ou 10x sem juros no cartão.\n• Início das aulas: Próxima segunda-feira às 19h.\n• Certificado oficial emitido ao final.",
        height=130
    )
    
    st.markdown("---")
    st.subheader("🎯 2. Termômetro de Lead Scoring")
    
    historico_texto = " ".join([m["content"] for m in st.session_state["chat_messages"] if m["role"] == "user"]).lower()
    
    score = 10
    if any(w in historico_texto for w in ["preco", "preço", "quanto", "pagamento", "cartao", "cartão", "parcela", "desconto"]):
        score += 40
    if any(w in historico_texto for w in ["inscricao", "inscrição", "matricula", "matrícula", "comprar", "quero", "fechar"]):
        score += 35
    if any(w in historico_texto for w in ["whatsapp", "fone", "telefone", "email", "@", "contato"]):
        score += 25
        
    score = min(score, 100)
    
    if score >= 75:
        st.success(f"🔥 **Lead Quente (Score: {score}/100)**: Alta intenção de compra identificada! Encaminhar para vendedor humano.")
    elif score >= 40:
        st.warning(f"⛅ **Lead Morno (Score: {score}/100)**: Tirando dúvidas de produto e valores.")
    else:
        st.info(f"❄️ **Lead Frio (Score: {score}/100)**: Apenas iniciando o contato inicial.")
        
    if st.button("🧹 Limpar e Reiniciar Chat", use_container_width=True):
        st.session_state["chat_messages"] = [
            {"role": "assistant", "content": f"Olá! 👋 Sou {nome_bot}, assistente virtual da {empresa}. Como posso te ajudar hoje?"}
        ]
        st.rerun()

with col_chat:
    st.subheader(f"💬 Simulador de Atendimento ao Vivo • {nome_bot}")
    
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    user_input = st.chat_input("Digite sua mensagem para testar o assistente (ex: Qual o valor do curso?)...")
    
    if user_input:
        st.session_state["chat_messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
            
        with st.chat_message("assistant"):
            with st.spinner(f"{nome_bot} está digitando..."):
                system_instruction = f"""
                Você é {nome_bot}, assistente virtual de atendimento e vendas da empresa '{empresa}'.
                Seu tom de voz é: {tom_bot}.
                Use a seguinte base de conhecimento para responder às perguntas do cliente de forma precisa, cordial e focada em conversão:
                {faq_conhecimento}
                
                Instruções:
                1. Seja conciso, amigável e persuasivo (máximo 3 a 4 frases).
                2. Adapte a resposta de acordo com a pergunta exata do cliente e o histórico da conversa.
                3. Sempre que o cliente demonstrar interesse, convide-o a deixar o nome e WhatsApp para concluir a inscrição ou receber material.
                4. Se não souber responder com base no FAQ, seja educado e solicite o contato para um consultor entrar em contato.
                """
                
                resposta = generate_text_ai(user_input, system_instruction, chat_history=st.session_state["chat_messages"])
                
                if not resposta:
                    resposta = generate_chatbot_offline_reply(
                        user_input=user_input,
                        empresa=empresa,
                        nome_bot=nome_bot,
                        tom_bot=tom_bot,
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
        ("3. Avaliação de Qualificação de Lead", f"<p><strong>Lead Score Final:</strong> {score}/100 ({'Quente' if score >= 75 else 'Morno' if score >= 40 else 'Frio'})</p>")
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

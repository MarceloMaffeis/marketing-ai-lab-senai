import streamlit as st
from utils.auth import check_authentication
from utils.ai_helper import render_api_key_sidebar, generate_text_ai
from utils.export_helper import generate_html_report, render_download_button

st.set_page_config(page_title="Chatbot & Automação | SENAI", page_icon="🤖", layout="wide")
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
    
    # Análise de intenção baseada no histórico de mensagens
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
    
    # Renderiza mensagens anteriores
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    # Entrada do usuário (aluno fingindo ser cliente)
    user_input = st.chat_input("Digite sua mensagem para testar o assistente (ex: Qual o valor do curso?)...")
    
    if user_input:
        # Registra mensagem do usuário
        st.session_state["chat_messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
            
        # Gera resposta do bot
        with st.chat_message("assistant"):
            with st.spinner(f"{nome_bot} está digitando..."):
                system_instruction = f"""
                Você é {nome_bot}, assistente virtual de atendimento e vendas da empresa '{empresa}'.
                Seu tom de voz é: {tom_bot}.
                Use a seguinte base de conhecimento para responder às perguntas do cliente de forma precisa, cordial e focada em conversão:
                {faq_conhecimento}
                
                Instruções:
                1. Seja conciso (máximo 3 a 4 frases).
                2. Sempre que apropriado, convide o usuário para deixar o nome e WhatsApp para formalizar a matrícula ou receber o material gratuito.
                3. Se não souber a resposta, seja gentil e informe que um consultor entrará em contato.
                """
                
                resposta = generate_text_ai(user_input, system_instruction)
                
                # Fallback heurístico offline
                if not resposta:
                    u_lower = user_input.lower()
                    if any(w in u_lower for w in ["preco", "preço", "valor", "custa", "investimento"]):
                        resposta = f"O investimento do curso é de R$ 490,00 ou em até 10x sem juros no cartão de crédito! 💳 Gostaria que eu reservasse a sua vaga ou prefere que eu envie a ementa detalhada pelo WhatsApp?"
                    elif any(w in u_lower for w in ["data", "quando", "inicio", "início", "horario", "horário"]):
                        resposta = f"Nossa próxima turma inicia na próxima segunda-feira, com aulas no período noturno (19h às 22h). As vagas são limitadas para garantir o aprendizado prático no laboratório!"
                    elif any(w in u_lower for w in ["certificado", "diploma", "reconhecido"]):
                        resposta = f"Sim! Ao concluir as 30 horas de capacitação você recebe o certificado oficial reconhecido pelo SENAI, com validade em todo o território nacional."
                    elif any(w in u_lower for w in ["sim", "quero", "como faco", "como faço", "matricula", "matrícula"]):
                        resposta = f"Excelente decisão! 🎉 Por favor, digite seu **Nome completo e WhatsApp com DDD** para que nossa equipe libere seu acesso imediatamente."
                    elif "@" in u_lower or any(char.isdigit() for char in u_lower):
                        resposta = f"Perfeito! Dados registrados com sucesso. Um de nossos consultores de atendimento entrará em contato em instantes para concluir sua inscrição. Muito obrigado pelo contato!"
                    else:
                        resposta = f"Entendi perfeitamente! Na {empresa}, estamos prontos para ajudar você a dominar as principais ferramentas de IA para marketing. Você gostaria de conhecer o programa de aulas ou falar sobre condições especiais de pagamento?"

                st.write(resposta)
                st.session_state["chat_messages"].append({"role": "assistant", "content": resposta})
                st.rerun()

    # Seção de Exportação da Transcrição
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

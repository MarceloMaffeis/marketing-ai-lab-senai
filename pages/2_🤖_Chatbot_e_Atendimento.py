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

st.title("🤖 Construtor de Chatbot de Atendimento, RAG & Lead Scoring")
st.caption("Alinhado ao **Módulo 1 da Ementa SENAI**: Automação de marketing, chatbots de atendimento, assistentes virtuais, tratamento de objeções, RAG (Base de Conhecimento) e qualificação de clientes para **qualquer negócio ou projeto**.")

# -------------------------------------------------------------
# DICIONÁRIO DE MODELOS DE NEGÓCIO / PRESETS
# -------------------------------------------------------------
BUSINESS_PRESETS = {
    "🎓 Cursos & Educação (SENAI / Formações)": {
        "nome": "Sofia",
        "papel": "Consultora Educacional & Relacionamento",
        "empresa": "Escola SENAI Sorocaba",
        "segmento": "Educação & Capacitação Técnica",
        "tom": "Consultivo & Empático (Especialista)",
        "faq": "• Cursos disponíveis: Marketing Digital com IA (30h) e Automação Industrial.\n• Investimento: R$ 490,00 em até 10x sem juros no cartão ou 10% de desconto no Pix.\n• Início das aulas: Próxima segunda-feira às 19h (Laboratório de Informática 3).\n• Requisitos: Ensino Fundamental completo e conhecimento básico de informática.\n• Certificado: Certificado Oficial SENAI-SP com validade nacional emitido ao final."
    },
    "🛍️ E-commerce & Loja de Roupas (Moda Urbana)": {
        "nome": "Camila",
        "papel": "Consultora de Estilo & Vendas Online",
        "empresa": "Bella Urbana Modas",
        "segmento": "E-commerce de Moda & Acessórios",
        "tom": "Descontraído & Amigável",
        "faq": "• Produtos em Destaque: Vestido Linho Casual (R$ 149,90), Calça Pantalona Alfaiataria (R$ 189,90) e Cropped Canelado (R$ 59,90).\n• Formas de Pagamento: Cartão de Crédito em até 6x sem juros ou Pix com 5% de desconto.\n• Prazos de Entrega: Sedex (1 a 3 dias úteis) e PAC (5 a 8 dias úteis). Frete Grátis para compras acima de R$ 250,00.\n• Política de Troca: 1ª troca 100% grátis em até 30 dias após o recebimento.\n• Tabela de Tamanhos: Do P ao GG com guia de medidas disponível."
    },
    "💈 Barbearia & Salão (Serviços e Agendamentos)": {
        "nome": "Lucas",
        "papel": "Atendente de Agendamento & Recepção",
        "empresa": "Barber Club Sorocaba",
        "segmento": "Serviços de Estética & Bem-Estar",
        "tom": "Descontraído & Amigável",
        "faq": "• Serviços & Preços: Corte Clássico (R$ 45,00), Barboterapia com Toalha Quente (R$ 40,00), Combo Cabelo + Barba (R$ 75,00) e Selagem Capilar (R$ 90,00).\n• Horário de Atendimento: Terça a Sábado das 09h às 20h. Domingo das 09h às 14h.\n• Endereço: Av. Dom Aguirre, 1500 - Centro (com estacionamento próprio gratuito).\n• Agendamentos: Envie seu Nome, Dia e Horário desejado para confirmação instantânea.\n• Cortesia: Chopp artesanal ou café expresso cortesia para todos os clientes!"
    },
    "🏥 Clínica Médica & Odontológica": {
        "nome": "Dra. Beatriz",
        "papel": "Triagem & Atendimento ao Paciente",
        "empresa": "Clínica Sorriso & Saúde Integrada",
        "segmento": "Saúde & Cuidados Médicos/Odonto",
        "tom": "Consultivo & Empático (Especialista)",
        "faq": "• Especialidades: Clínica Geral, Odontologia Estética (Clareamento e Lentes), Implantes e Ortodontia (Invisalign).\n• Avaliação Inicial: Consulta de diagnóstico e raio-X panorâmico com agendamento prévio.\n• Convênios & Pagamento: Aceitamos Unimed, Amil, SulAmérica e parcelamento particular em até 12x no cartão.\n• Horário de Funcionamento: Segunda a Sexta das 08h às 19h e Sábados das 08h às 13h.\n• Localização: Rua das Palmeiras, 320 - Sala 402, Campolim."
    },
    "🏠 Imobiliária & Locação / Venda": {
        "nome": "Rodrigo",
        "papel": "Consultor Imobiliário & Negócios",
        "empresa": "Prime Imóveis & Investimentos",
        "segmento": "Imobiliário & Construção Civil",
        "tom": "Vendedor Direto & Focado em Fechamento",
        "faq": "• Imóveis em Destaque: Apartamento 2 Dorms (1 Suíte) no Campolim (Venda R$ 420.000 / Aluguel R$ 2.400/mês), Casa em Condomínio Fechado 3 Suítes (R$ 890.000) e Salas Comerciais para locação (R$ 1.500/mês).\n• Condições de Compra: Aceita Financiamento Caixa/Itaú, FGTS e estuda permuta por veículo.\n• Locação sem Fiador: Opções com Seguro Fiança ou Cartão de Crédito CredPago sem burocracia.\n• Agendamento de Visitas: Visitas acompanhadas de Segunda a Sábado com horário flexível."
    },
    "🍕 Restaurante / Pizzaria & Delivery": {
        "nome": "Giovanni",
        "papel": "Atendente de Pedidos & Delivery",
        "empresa": "Bella Napoli Pizzaria Forno a Lenha",
        "segmento": "Gastronomia & Delivery",
        "tom": "Descontraído & Amigável",
        "faq": "• Cardápio Destaques: Pizza Margherita Especial (R$ 68,00), Pizza Calabresa Gourmet (R$ 62,00), Pizza Quatro Queijos Tradicional (R$ 72,00) e Pizza Doce Nutella com Morango (R$ 55,00).\n• Borda Recheada: Catupiry Original (+ R$ 12,00) ou Cheddar (+ R$ 10,00).\n• Tempo de Entrega: Média de 35 a 50 minutos. Retirada no balcão em 25 minutos.\n• Taxa de Entrega: R$ 7,00 (Grátis para pedidos acima de R$ 100,00).\n• Formas de Pagamento: Pix, Cartão de Débito/Crédito na entrega ou VR/VA (Alelo, Sodexo, Ticket)."
    },
    "🚀 Agência de Marketing Digital & B2B": {
        "nome": "Renan",
        "papel": "Estrategista de Vendas B2B",
        "empresa": "Scale Digital Performance",
        "segmento": "Marketing Digital & Soluções B2B",
        "tom": "Vendedor Direto & Focado em Fechamento",
        "faq": "• Planos de Gestão: Plano Growth (Gestão de Meta Ads + Google Ads a partir de R$ 1.200/mês), Plano Enterprise (Tráfego + Funis de IA + CRM por R$ 2.800/mês).\n• O que está incluso: Criação de criativos, copywriting, testes A/B, dashboards de BI e reuniões quinzenais de alinhamento de ROI.\n• Contrato & Prazos: Sem taxa de adesão, contrato mínimo de 3 meses para validação de esteira.\n• Diagnóstico Gratuito: Agende uma sessão estratégica de 30 minutos com nossos especialistas."
    },
    "✨ Projeto Personalizado (Crie do Zero)": {
        "nome": "Alex",
        "papel": "Especialista de Atendimento",
        "empresa": "Minha Empresa / Startup",
        "segmento": "Negócio Personalizado",
        "tom": "Consultivo & Empático (Especialista)",
        "faq": "• Produtos/Serviços: Descreva aqui seus principais produtos ou serviços oferecidos.\n• Preços & Condições: Descreva valores, formas de pagamento (Pix, Cartão, Boleto) e parcelamento.\n• Prazos & Horários: Descreva dias de atendimento, horário de funcionamento ou prazos de entrega/execução.\n• Políticas & Garantias: Informações sobre trocas, devoluções, suporte e diferenciais da sua marca."
    }
}

col_config, col_chat = st.columns([1, 2], gap="large")

with col_config:
    st.subheader("⚙️ 1. Configuração do Negócio & Persona")
    
    preset_escolhido = st.selectbox(
        "Carregar Modelo de Negócio (Template Rápido):",
        list(BUSINESS_PRESETS.keys()),
        index=0,
        help="Selecione um exemplo pronto de mercado ou personalize livremente para o projeto da sua aula."
    )
    
    preset_data = BUSINESS_PRESETS[preset_escolhido]
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        nome_bot = st.text_input("Nome do Atendente (Persona):", value=preset_data["nome"])
    with col_p2:
        papel_bot = st.text_input("Papel / Cargo:", value=preset_data["papel"])
        
    empresa = st.text_input("Nome da Empresa / Marca / Projeto:", value=preset_data["empresa"])
    segmento = st.text_input("Segmento / Nicho do Negócio:", value=preset_data["segmento"])
    
    tom_opcoes = [
        "Consultivo & Empático (Especialista)",
        "Vendedor Direto & Focado em Fechamento",
        "Técnico & Preciso",
        "Descontraído & Amigável",
        "Luxo & Exclusivo"
    ]
    idx_tom = tom_opcoes.index(preset_data["tom"]) if preset_data["tom"] in tom_opcoes else 0
    tom_bot = st.selectbox("Tom de Voz do Atendimento:", tom_opcoes, index=idx_tom)
    
    st.markdown("#### 📚 RAG: Base de Conhecimento da Empresa")
    st.caption("Insira o catálogo de produtos/serviços, tabela de preços, prazos, cardápio, regras de frete e políticas da marca.")
    
    faq_conhecimento = st.text_area(
        "Base de Conhecimento / Catálogo / FAQs:",
        value=preset_data["faq"],
        height=160
    )

    # Assinatura da configuração atual para detectar mudanças e resetar memória
    config_sig = f"{nome_bot.strip()}|{papel_bot.strip()}|{empresa.strip()}|{segmento.strip()}|{tom_bot}|{faq_conhecimento.strip()}"
    
    # Auto-inicialização e Sincronização Automática de Memória
    if "chat_config_sig" not in st.session_state:
        st.session_state["chat_config_sig"] = config_sig
        st.session_state["chat_messages"] = [
            {"role": "assistant", "content": f"Olá! 👋 Sou {nome_bot}, {papel_bot.lower()} da {empresa}. Como posso te ajudar hoje?"}
        ]
    elif st.session_state["chat_config_sig"] != config_sig:
        st.session_state["chat_config_sig"] = config_sig
        st.session_state["chat_messages"] = [
            {"role": "assistant", "content": f"Olá! 👋 Sou {nome_bot}, {papel_bot.lower()} da {empresa}. Como posso te ajudar hoje?"}
        ]
        st.toast(f"🔄 Assistente '{nome_bot}' ({empresa}) reconfigurado!", icon="✨")
    
    st.markdown("---")
    st.subheader("🎯 2. Termômetro de Lead Scoring (IA)")
    
    # Análise de sinais positivos e objeções do diálogo
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
            
    if st.button("🧹 Limpar Histórico do Chat", use_container_width=True):
        st.session_state["chat_messages"] = [
            {"role": "assistant", "content": f"Olá! 👋 Sou {nome_bot}, {papel_bot.lower()} da {empresa}. Como posso te ajudar hoje?"}
        ]
        st.rerun()

with col_chat:
    status_ia = "🟢 Conectado ao Google Gemini" if get_api_key() else "⚡ Modo Inteligente Offline"
    
    col_chat_title, col_chat_reset = st.columns([3, 1])
    with col_chat_title:
        st.subheader(f"💬 Simulador de Atendimento ao Vivo • {nome_bot}")
        st.caption(f"Status da IA: **{status_ia}** | Empresa: **{empresa}** ({segmento}) | Tom: **{tom_bot.split('(')[0].strip()}**")
    with col_chat_reset:
        if st.button("🧹 Reiniciar Conversa", key="btn_reset_chat_top", use_container_width=True, help="Reinicia a conversa com a persona configurada"):
            st.session_state["chat_messages"] = [
                {"role": "assistant", "content": f"Olá! 👋 Sou {nome_bot}, {papel_bot.lower()} da {empresa}. Como posso te ajudar hoje?"}
            ]
            st.rerun()
    
    # Exibição do histórico de mensagens
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    # Botões de testes rápidos universais para os alunos
    st.markdown("<p style='font-size: 0.85rem; color: #888; margin-top: 15px; margin-bottom: 5px;'>⚡ <strong>Simulações Rápidas de Clientes (Clique para testar):</strong></p>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    quick_msg = None
    with c1:
        if st.button("🛍️ Quais opções/produtos?", use_container_width=True):
            quick_msg = "Quais produtos ou serviços vocês oferecem?"
    with c2:
        if st.button("🕒 Horários / Prazos?", use_container_width=True):
            quick_msg = "Quais os horários de atendimento, prazos e endereço?"
    with c3:
        if st.button("💰 Quanto custa e pagamento?", use_container_width=True):
            quick_msg = "Qual o valor e quais as formas de pagamento disponíveis?"
    with c4:
        if st.button("❌ Achei muito caro", use_container_width=True):
            quick_msg = "Achei muito caro, não quero nenhum desses."
            
    user_input = st.chat_input("Digite sua mensagem para testar o assistente...")
    if quick_msg:
        user_input = quick_msg
    
    if user_input:
        st.session_state["chat_messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
            
        with st.chat_message("assistant"):
            with st.spinner(f"{nome_bot} está digitando..."):
                system_instruction = f"""
                Você é {nome_bot}, {papel_bot} da empresa {empresa} (Segmento: {segmento}).
                Você atende clientes de forma 100% humanizada, empática, inteligente e conversacional.
                
                DIRETRIZES DE PERSONA & ATENDIMENTO:
                1. Tom de voz configurado: {tom_bot}.
                2. Base de Conhecimento e Catálogo Oficial da Empresa (RAG):
                {faq_conhecimento}
                
                REGRAS CRUCIAIS DE CONVERSAÇÃO:
                - Responda SEMPRE com base estrita no catálogo e regras da {empresa} descritos acima. Se o cliente perguntar de itens não listados, esclareça gentilmente quais opções estão disponíveis no momento sem inventar dados.
                - SE O CLIENTE REJEITAR OU DISSER 'NÃO QUERO', 'NÃO TENHO INTERESSE', 'MUITO CARO':
                  - NUNCA force a compra/contratação e NUNCA ignore a recusa! Seja empático, acolhedor e pergunte se ele deseja receber novidades ou opções futuras.
                - SE O CLIENTE DEMONSTRAR INTERESSE REAL (preço, prazos, agendamento, compra):
                  - Explique com clareza os diferenciais e convide-o a enviar Nome e WhatsApp para concluir o pedido/reserva.
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
                        history=st.session_state["chat_messages"],
                        papel_bot=papel_bot,
                        segmento=segmento
                    )

                st.write(resposta)
                st.session_state["chat_messages"].append({"role": "assistant", "content": resposta})
                st.rerun()

    with st.expander("🎓 Por Dentro da IA: System Prompt & Engenharia de RAG desta Persona", expanded=False):
        st.markdown(f"""
        **Como o Chatbot processa essa configuração:**
        - **Persona:** `{nome_bot}` ({papel_bot}) da `{empresa}`
        - **Nicho:** `{segmento}` | **Tom:** `{tom_bot}`
        - **Contexto RAG Ativo:** `{len(faq_conhecimento.splitlines())} regras/linhas de catálogo carregadas.`
        - **Modelo de Lead Scoring:** Net Score dinâmico (Engajamento + Sondagem Financeira + Objeções + Intenção de Compra).
        """)
        st.code(f"""# System Prompt gerado dinamicamente para o modelo de IA:
Você é {nome_bot}, {papel_bot} da empresa {empresa} (Segmento: {segmento}).
Tom de Voz: {tom_bot}

Base de Conhecimento (RAG):
{faq_conhecimento}
""", language="markdown")

    st.markdown("---")
    st.subheader("📥 Exportar Transcrição do Atendimento")
    
    transcricao_html = "<div style='font-family: monospace;'>"
    for m in st.session_state["chat_messages"]:
        autor = f"<strong>{nome_bot} ({papel_bot}):</strong>" if m["role"] == "assistant" else "<strong>Cliente:</strong>"
        transcricao_html += f"<p>{autor} {m['content']}</p>"
    transcricao_html += "</div>"
    
    secoes_chat = [
        ("1. Perfil do Projeto & Persona Configurada", f"<p><strong>Assistente:</strong> {nome_bot} ({papel_bot})<br><strong>Empresa:</strong> {empresa}<br><strong>Segmento:</strong> {segmento}<br><strong>Tom de Voz:</strong> {tom_bot}</p>"),
        ("2. Base de Conhecimento (RAG)", f"<pre style='background:#f4f4f4; padding:10px; border-radius:5px;'>{faq_conhecimento}</pre>"),
        ("3. Transcrição Completa da Conversa", transcricao_html),
        ("4. Avaliação de Qualificação de Lead (Lead Scoring)", f"<p><strong>Status:</strong> {analise_scoring['classificacao']}<br><strong>Pontos Positivos:</strong> +{analise_scoring['pontos_positivos']} pts<br><strong>Penalidades/Objeções:</strong> -{analise_scoring['penalidades']} pts</p>")
    ]
    
    html_chat = generate_html_report(
        title=f"Relatório de Atendimento & Lead Scoring: {empresa} ({nome_bot})",
        subtitle=f"Projeto de Chatbot com RAG - Segmento: {segmento}",
        sections=secoes_chat
    )
    
    render_download_button(
        label="📥 Baixar Transcrição e Diagnóstico de Lead em HTML",
        data=html_chat,
        file_name=f"projeto_chatbot_{empresa.lower().replace(' ', '_')}.html",
        mime="text/html"
    )

render_sidebar_footer()
render_academic_footer()


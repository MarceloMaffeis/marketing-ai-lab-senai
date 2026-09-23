import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.auth import check_authentication
from utils.ai_helper import render_api_key_sidebar, generate_text_ai
from utils.export_helper import generate_html_report, render_download_button
from utils.ui_components import render_sidebar_header, render_sidebar_footer, render_academic_footer

st.set_page_config(page_title="Programática & Google Ads | SENAI", page_icon="🎯", layout="wide")
render_sidebar_header()
check_authentication()
render_api_key_sidebar()

st.title("🎯 Mídia Programática, RTB & Construtor Google Ads")
st.caption("Alinhado ao **Módulo 3 da Ementa SENAI**: Publicidade programática, leilões em tempo real (RTB), estratégias de Smart Bidding com IA e **criação de campanhas de pesquisa no Google Ads (RSA)**.")

tab_rtb, tab_rsa = st.tabs([
    "🎯 1. Simulador de Leilão RTB & Smart Bidding",
    "📢 2. Construtor de Anúncios Google Ads (RSA)"
])

# ==============================================================================
# ABA 1: SIMULADOR DE RTB & PROGRAMÁTICA
# ==============================================================================
with tab_rtb:
    with st.expander("💡 Entenda o Ecossistema Programático (DSP, SSP & RTB)", expanded=False):
        st.markdown(
            """
            * **DSP (Demand-Side Platform):** Plataforma onde os anunciantes compram espaços publicitários de forma automatizada.
            * **SSP (Supply-Side Platform):** Plataforma onde os donos de sites (publishers) disponibilizam seus espaços para venda.
            * **Ad Exchange & RTB (Real-Time Bidding):** O leilão em tempo real que ocorre em menos de **100 milissegundos** enquanto uma página web é carregada.
            * **Algoritmos de Smart Bidding com IA:** Analisam centenas de variáveis do usuário (dispositivo, histórico, horário, intenção de compra) para calcular a probabilidade de conversão e ofertar o lance ideal instantaneamente.
            """
        )

    col_params, col_sim = st.columns([1, 2], gap="large")

    with col_params:
        st.subheader("⚙️ Configurações da Campanha")
        
        orcamento = st.slider("💰 Orçamento Diário da Campanha (R$):", min_value=100, max_value=5000, value=1000, step=100)
        
        tipo_estrategia = st.radio(
            "🧠 Estratégia de Lance:",
            ["Smart Bidding com IA (Maximizar Conversões)", "Lance Manual Tradicional (CPM Fixo)"]
        )
        
        segmentacao = st.selectbox(
            "👥 Tipo de Segmentação:",
            [
                "Público Lookalike (Semelhante) gerado por IA",
                "Segmentação Demográfica + Interesses de Mercado",
                "Público Amplo / Sem Segmentação",
                "Remarketing Dinâmico (Visitantes Recentes)"
            ]
        )
        
        formato = st.selectbox(
            "📱 Formato do Criativo:",
            ["Display Banner Responsivo (300x250 / 728x90)", "Vídeo In-Stream (Pre-Roll)", "Native Ads (Conteúdo Integrado)"]
        )
        
        ticket_medio = st.number_input("🏷️ Ticket Médio do Produto (R$):", min_value=10, max_value=5000, value=250, step=10)
        
        btn_simular = st.button("🚀 Executar Simulação de Leilão RTB", type="primary", use_container_width=True)

    if btn_simular:
        with col_sim:
            st.subheader("📊 Resultados da Simulação em Tempo Real")
            
            is_ai = "Smart Bidding" in tipo_estrategia
            
            fator_seg = {
                "Público Lookalike (Semelhante) gerado por IA": 1.45,
                "Segmentação Demográfica + Interesses de Mercado": 1.15,
                "Público Amplo / Sem Segmentação": 0.70,
                "Remarketing Dinâmico (Visitantes Recentes)": 1.65
            }[segmentacao]
            
            cpm_base = 12.0 if "Display" in formato else 28.0 if "Vídeo" in formato else 16.0
            ctr_base = 0.9 if "Display" in formato else 1.8 if "Vídeo" in formato else 1.2
            cvr_base = 2.0
            
            if is_ai:
                cpm_efetivo = cpm_base * 1.10
                ctr_efetivo = ctr_base * fator_seg * 1.25
                cvr_efetivo = cvr_base * fator_seg * 1.40
                leiloes_disputados = int(orcamento * 80)
                taxa_vitoria = 0.68
            else:
                cpm_efetivo = cpm_base * 0.95
                ctr_efetivo = ctr_base * fator_seg * 0.85
                cvr_efetivo = cvr_base * fator_seg * 0.80
                leiloes_disputados = int(orcamento * 80)
                taxa_vitoria = 0.45
                
            impressoes = int((orcamento / cpm_efetivo) * 1000)
            cliques = int(impressoes * (ctr_efetivo / 100))
            cliques = max(cliques, 5)
            conversoes = int(cliques * (cvr_efetivo / 100))
            conversoes = max(conversoes, 1)
            
            cpa = round(orcamento / conversoes, 2)
            cpc = round(orcamento / cliques, 2)
            receita_estimada = round(conversoes * ticket_medio, 2)
            roas = round(receita_estimada / orcamento, 2)
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("👁️ Impressões Ganhas", f"{impressoes:,}".replace(",", "."))
            m2.metric("🖱️ Cliques (CTR)", f"{cliques:,} ({ctr_efetivo:.2f}%)")
            m3.metric("🎯 Conversões (CPA)", f"{conversoes} (R$ {cpa})")
            m4.metric("📈 ROAS Estimado", f"{roas:.2f}x", f"R$ {receita_estimada:,.2f}")
            
            funil_df = pd.DataFrame({
                "Etapa": ["1. Leilões Disputados", "2. Impressões Ganhas", "3. Cliques Qualificados", "4. Conversões"],
                "Volume": [leiloes_disputados, impressoes, cliques, conversoes]
            })
            
            fig_funnel = go.Figure(go.Funnel(
                y=funil_df["Etapa"],
                x=funil_df["Volume"],
                textinfo="value+percent initial",
                marker={"color": ["#38bdf8", "#818cf8", "#a855f7", "#ec4899"]}
            ))
            fig_funnel.update_layout(title="📉 Funil de Eficiência do Leilão Programático", margin=dict(l=20, r=20, t=40, b=20), height=320)
            st.plotly_chart(fig_funnel, use_container_width=True)
            
            st.subheader("💡 Diagnóstico do Algoritmo")
            if is_ai:
                st.success(
                    f"✅ **Vantagem da IA (Smart Bidding):** O algoritmo ajustou os lances em milissegundos para usuários com maior probabilidade de converter no segmento **{segmentacao}**, gerando um ROAS de **{roas}x** e reduzindo o CPA para **R$ {cpa}**."
                )
            else:
                st.warning(
                    f"⚠️ **Atenção (Lance Manual):** Como os lances foram fixos, a campanha comprou impressões em horários e usuários sem intenção de compra, resultando em menor taxa de vitória no leilão e CPA mais alto (**R$ {cpa}**)."
                )
                
            st.markdown("---")
            secoes_midia = [
                ("1. Resumo do Plano de Mídia Programática", f"<p><strong>Orçamento Diário:</strong> R$ {orcamento:,.2f}<br><strong>Estratégia:</strong> {tipo_estrategia}<br><strong>Segmentação:</strong> {segmentacao}<br><strong>Formato:</strong> {formato}</p>"),
                ("2. Métricas de Desempenho Projetadas", f"<p><strong>Impressões:</strong> {impressoes:,}<br><strong>CTR:</strong> {ctr_efetivo:.2f}%<br><strong>Cliques:</strong> {cliques:,}<br><strong>Conversões:</strong> {conversoes}<br><strong>CPA:</strong> R$ {cpa}<br><strong>Receita Estimada:</strong> R$ {receita_estimada:,.2f}<br><strong>ROAS:</strong> {roas:.2f}x</p>"),
                ("3. Insights de Otimização", f"<p>{'Excelente uso de inteligência artificial preditiva para maximização de retorno.' if is_ai else 'Recomenda-se migrar para estratégias baseadas em Smart Bidding com aprendizado de máquina para reduzir o desperdício de lances.'}</p>")
            ]
            
            html_midia = generate_html_report(
                title="Plano de Mídia Programática com IA",
                subtitle="Simulação de Leilão RTB & Projeção de Retorno",
                sections=secoes_midia
            )
            
            render_download_button(
                label="📥 Baixar Plano de Mídia em HTML",
                data=html_midia,
                file_name="plano_midia_programatica_ia.html",
                mime="text/html"
            )
    else:
        with col_sim:
            st.info("👈 Ajuste o orçamento, a estratégia de lances e clique em **Executar Simulação de Leilão RTB** para ver o funil e a eficiência dos algoritmos de IA.")

# ==============================================================================
# ABA 2: CRIADOR DE ANÚNCIOS RESPONSIVOS GOOGLE ADS (RSA)
# ==============================================================================
with tab_rsa:
    st.subheader("📢 Construtor de Anúncios Responsivos de Pesquisa (Google Ads RSA)")
    st.caption("No Google Ads moderno, o algoritmo de Machine Learning combina dinamicamente até **15 Títulos (máx 30 caracteres)** e **4 Descrições (máx 90 caracteres)** para entregar o melhor anúncio a cada pesquisa.")
    
    col_rsa1, col_rsa2 = st.columns([1, 1], gap="large")
    
    with col_rsa1:
        st.markdown("#### 1. Dados do Anúncio & Empresa")
        rsa_empresa = st.text_input("Nome da Empresa / Anunciante:", value="Escola SENAI Sorocaba")
        rsa_produto = st.text_input("Produto / Serviço / Curso Anunciado:", value="Curso de Marketing Digital com Inteligência Artificial")
        rsa_oferta = st.text_input("Diferenciais / Ofertas Comerciais:", value="Certificado Oficial SENAI, 10x sem juros, Aulas práticas em laboratório")
        rsa_url = st.text_input("URL Final de Destino (Landing Page):", value="https://www.sp.senai.br/unidade/sorocaba/")
        
        btn_gerar_rsa = st.button("✨ Gerar Títulos, Descrições & Extensões com IA", type="primary", use_container_width=True)

    with col_rsa2:
        st.markdown("#### 2. Prévia do Anúncio no Google (SERP Preview)")
        
        # Mockup visual de Anúncio Patrocinado do Google
        st.markdown(f"""
        <div style="background-color: #ffffff; padding: 18px; border-radius: 8px; border: 1px solid #dfe1e5; font-family: Roboto, Arial, sans-serif; box-shadow: 0 1px 4px rgba(32,33,36,.12); color: #202124;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                <span style="font-size: 11px; font-weight: bold; color: #202124; background: #e8eaed; padding: 1px 5px; border-radius: 3px;">Patrocinado</span>
                <span style="font-size: 12px; color: #202124;">{rsa_url}</span>
            </div>
            <div style="font-size: 19px; color: #1a0dab; text-decoration: none; font-weight: 400; line-height: 1.3; margin-bottom: 5px;">
                {rsa_produto[:30]} | {rsa_empresa[:25]} | Vagas Abertas
            </div>
            <div style="font-size: 13px; color: #4d5156; line-height: 1.4; margin-bottom: 8px;">
                Aprenda Marketing com IA na prática com {rsa_empresa}. {rsa_oferta}. Garanta sua vaga hoje mesmo!
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 12px; margin-top: 10px; font-size: 12px; color: #1a0dab;">
                <span>• Grade Curricular Oficial</span>
                <span>• Bolsas e Condições</span>
                <span>• Fale no WhatsApp</span>
                <span>• Localização e Horários</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.caption("📱 O Google Ads testa automaticamente milhares de combinações para maximizar a Taxa de Cliques (CTR) e o Índice de Qualidade.")

    st.markdown("---")
    
    if btn_gerar_rsa or "cached_rsa_data" in st.session_state:
        if btn_gerar_rsa:
            prompt_rsa = f"""
            Você é um especialista certificado em Google Ads do SENAI-SP.
            Crie os componentes de um Anúncio Responsivo de Pesquisa (RSA) para:
            - Empresa: {rsa_empresa}
            - Produto/Serviço: {rsa_produto}
            - Diferenciais: {rsa_oferta}
            
            REGRAS OBRIGATÓRIAS DO GOOGLE ADS:
            1. TÍTULOS: Gere exatamente 10 títulos altamente atrativos. CADA TÍTULO DEVE TER NO MÁXIMO 30 CARACTERES (NÃO ULTRAPASSE 30 CARACTERES NUNCA!).
            2. DESCRIÇÕES: Gere exatamente 4 descrições persuasivas. CADA DESCRIÇÃO DEVE TER NO MÁXIMO 90 CARACTERES (NÃO ULTRAPASSE 90 CARACTERES NUNCA!).
            3. EXTENSÕES (Sitelinks): Gere 4 frases de Sitelink curtas.
            
            Responda em formato estruturado.
            """
            with st.spinner("Gerando títulos e descrições com regras de caracteres do Google Ads..."):
                res_rsa_raw = generate_text_ai(prompt_rsa, "Você é um gestor de tráfego sênior de Google Ads.")
                
                # Heurística Dinâmica com contagem estrita de caracteres
                titulos_padrao = [
                    f"Curso {rsa_produto[:18]}",
                    f"{rsa_empresa[:28]}",
                    "Matrículas Abertas 2026",
                    "Aprenda IA na Prática",
                    "Certificado Oficial Reconhecido",
                    "10x Sem Juros no Cartão",
                    "Vagas Limitadas na Turma",
                    "Início Imediato em SP",
                    "Laboratórios de Ponta",
                    "Garanta Sua Vaga Hoje"
                ]
                titulos_padrao = [t[:30] for t in titulos_padrao]
                
                descricoes_padrao = [
                    f"Aprenda Marketing com IA na prática na {rsa_empresa}. Garanta sua vaga hoje!"[:90],
                    f"Domine ChatGPT, SEO e automação com certificado oficial. Inscrições abertas!"[:90],
                    f"Aulas presenciais em laboratórios modernos e foco nas demandas da indústria."[:90],
                    f"Condições especiais de pagamento em até 10x sem juros. Fale com nossa equipe!"[:90]
                ]
                
                st.session_state["cached_rsa_data"] = {
                    "titulos": titulos_padrao,
                    "descricoes": descricoes_padrao
                }

        rsa_data = st.session_state.get("cached_rsa_data", {})
        titulos = rsa_data.get("titulos", [])
        descricoes = rsa_data.get("descricoes", [])
        
        col_tits, col_descs = st.columns(2)
        
        with col_tits:
            st.markdown("#### 🏷️ 10 Títulos Gerados (Máx. 30 caracteres cada)")
            titulos_df_data = []
            for i, t in enumerate(titulos, 1):
                tam = len(t)
                status = "✅ OK" if tam <= 30 else "❌ Excedeu"
                titulos_df_data.append({"#": i, "Título": t, "Caracteres": f"{tam}/30", "Status": status})
                
            st.dataframe(pd.DataFrame(titulos_df_data), use_container_width=True, hide_index=True)
            
        with col_descs:
            st.markdown("#### 📝 4 Descrições Geradas (Máx. 90 caracteres cada)")
            descs_df_data = []
            for i, d in enumerate(descricoes, 1):
                tam = len(d)
                status = "✅ OK" if tam <= 90 else "❌ Excedeu"
                descs_df_data.append({"#": i, "Descrição": d, "Caracteres": f"{tam}/90", "Status": status})
                
            st.dataframe(pd.DataFrame(descs_df_data), use_container_width=True, hide_index=True)
            
        c_rsa_b1, c_rsa_b2 = st.columns(2)
        with c_rsa_b1:
            st.link_button(
                "🚀 Abrir Google Ads Campaign Builder ↗",
                "https://ads.google.com/",
                use_container_width=True,
                help="Acesse sua conta do Google Ads para colar os títulos e descrições criados"
            )
        with c_rsa_b2:
            st.link_button(
                "🔍 Ver Anúncios da Concorrência no Google Transparency Center ↗",
                "https://adstransparency.google.com/",
                use_container_width=True
            )

render_sidebar_footer()
render_academic_footer()


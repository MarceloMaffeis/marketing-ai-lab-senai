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
from utils.ai_helper import render_api_key_sidebar
from utils.export_helper import generate_html_report, render_download_button
from utils.ui_components import render_sidebar_header, render_sidebar_footer, render_academic_footer

st.set_page_config(page_title="Simulador de Programática & RTB | SENAI", page_icon="🎯", layout="wide")
render_sidebar_header()
check_authentication()
render_api_key_sidebar()

st.title("🎯 Simulador de Publicidade Programática & Leilão RTB")
st.caption("Alinhado ao **Módulo 3 da Ementa SENAI**: Publicidade programática e IA, otimização de campanhas, segmentação e plataformas de lances.")

# Bloco explicativo didático sobre RTB
with st.expander("💡 Entenda o Ecossistema Programático (DSP, SSP & RTB)", expanded=False):
    st.markdown(
        """
        * **DSP (Demand-Side Platform):** Plataforma onde os anunciantes compram espaços publicitários de forma automatizada.
        * **SSP (Supply-Side Platform):** Plataforma onde os donos de sites (publishers) disponibilizam seus espaços para venda.
        * **Ad Exchange & RTB (Real-Time Bidding):** O leilão em tempo real que ocorre em menos de **100 milissegundos** enquanto uma página web é carregada.
        * **Algoritmos de Smart Bidding com IA:** Analisam centenas de variáveis do usuário (dispositivo, histórico, horário, intenção de compra) para calcular a probabilidade de conversão e ofertar o lance ideal instantaneamente.
        """
    )

st.markdown("---")

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

# Lógica da Simulação
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

render_sidebar_footer()
render_academic_footer()

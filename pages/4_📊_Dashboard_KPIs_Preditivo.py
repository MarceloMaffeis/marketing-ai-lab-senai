import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from utils.auth import check_authentication
from utils.ai_helper import render_api_key_sidebar
from utils.export_helper import generate_html_report, render_download_button
from utils.ui_components import render_sidebar_header, render_sidebar_footer, render_academic_footer

st.set_page_config(page_title="KPIs & Análise Preditiva | SENAI", page_icon="📊", layout="wide")
render_sidebar_header()
check_authentication()
render_api_key_sidebar()

st.title("📊 Dashboard de KPIs, Business Intelligence & Análise Preditiva")
st.caption("Alinhado aos **Módulos 2 e 6 da Ementa SENAI**: Análise de dados, Machine Learning, previsão de tendências, monitoramento de KPIs e melhoria contínua.")

st.markdown("---")

col_data_opt1, col_data_opt2 = st.columns([2, 1])

with col_data_opt1:
    uploaded_file = st.file_uploader("📂 Faça upload da planilha de campanhas (CSV):", type=["csv"], help="Pode ser um relatório extraído do Meta Ads, Google Ads ou seu CRM.")

with col_data_opt2:
    st.write("Ou utilize nossa base pedagógica de testes:")
    use_sample = st.button("📊 Carregar Base de Exemplo SENAI", use_container_width=True)

df = None
sample_path = os.path.join(ROOT_DIR, "data", "campanhas_exemplo.csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ Base de dados carregada com sucesso!")
    except Exception as e:
        st.error(f"Erro ao ler CSV: {e}")
elif os.path.exists(sample_path):
    df = pd.read_csv(sample_path)

if df is not None:
    with st.expander("🔍 Filtros de Segmentação e Canais", expanded=False):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            canais_disponiveis = df["Canal"].unique().tolist()
            filtro_canais = st.multiselect("Filtrar Canais:", canais_disponiveis, default=canais_disponiveis)
        with col_f2:
            segmentos_disponiveis = df["Segmento"].unique().tolist()
            filtro_segmentos = st.multiselect("Filtrar Segmentos:", segmentos_disponiveis, default=segmentos_disponiveis)

    df_filtrado = df[df["Canal"].isin(filtro_canais) & df["Segmento"].isin(filtro_segmentos)].copy()
    
    if df_filtrado.empty:
        st.warning("Nenhum dado corresponde aos filtros selecionados.")
        st.stop()

    total_gasto = df_filtrado["Gasto_R$"].sum()
    total_receita = df_filtrado["Receita_R$"].sum()
    total_conversoes = df_filtrado["Conversoes"].sum()
    total_cliques = df_filtrado["Cliques"].sum()
    total_impressoes = df_filtrado["Impressoes"].sum()
    
    roas_global = (total_receita / total_gasto) if total_gasto > 0 else 0
    cpa_medio = (total_gasto / total_conversoes) if total_conversoes > 0 else 0
    ctr_medio = (total_cliques / total_impressoes * 100) if total_impressoes > 0 else 0
    lucro_liquido = total_receita - total_gasto

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("💰 Total Investido", f"R$ {total_gasto:,.2f}")
    kpi2.metric("💵 Receita Gerada", f"R$ {total_receita:,.2f}", f"Lucro: R$ {lucro_liquido:,.2f}")
    kpi3.metric("🎯 ROAS Geral", f"{roas_global:.2f}x", "Retorno sobre Anúncio")
    kpi4.metric("🏷️ CPA Médio (CAC)", f"R$ {cpa_medio:.2f}", f"{total_conversoes} Conversões")
    kpi5.metric("🖱️ CTR Global", f"{ctr_medio:.2f}%", f"{total_cliques:,} Cliques")

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📈 Desempenho por Canal", "🗓️ Evolução Temporal", "🤖 Previsão com Machine Learning"])

    with tab1:
        st.subheader("Comparativo de Retorno (ROAS vs. CPA por Canal)")
        canal_metrics = df_filtrado.groupby("Canal").agg({
            "Gasto_R$": "sum",
            "Receita_R$": "sum",
            "Conversoes": "sum"
        }).reset_index()
        canal_metrics["ROAS"] = canal_metrics["Receita_R$"] / canal_metrics["Gasto_R$"]
        canal_metrics["CPA"] = canal_metrics["Gasto_R$"] / canal_metrics["Conversoes"]

        fig_bar = px.bar(
            canal_metrics,
            x="Canal",
            y="ROAS",
            color="ROAS",
            color_continuous_scale="Viridis",
            text_auto=".2f",
            title="ROAS (Multiplicador de Retorno) por Canal de Mídia"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        st.subheader("Evolução Diária de Receita e Investimento")
        daily_df = df_filtrado.groupby("Data").agg({"Gasto_R$": "sum", "Receita_R$": "sum"}).reset_index()
        
        fig_time = px.line(
            daily_df,
            x="Data",
            y=["Receita_R$", "Gasto_R$"],
            labels={"value": "Valor (R$)", "variable": "Métrica"},
            title="Tendência de Faturamento vs. Investimento Diário"
        )
        st.plotly_chart(fig_time, use_container_width=True)

    with tab3:
        st.subheader("🤖 Modelo Preditivo de Vendas e Otimização com IA")
        st.write("Utilizando regressão linear com **Machine Learning (Scikit-Learn)** para prever a receita futura com base em variações de orçamento:")
        
        X = df_filtrado[["Gasto_R$"]].values
        y = df_filtrado["Receita_R$"].values
        
        modelo = LinearRegression()
        modelo.fit(X, y)
        
        col_pred1, col_pred2 = st.columns([1, 2])
        with col_pred1:
            novo_orcamento = st.slider("Simular Novo Investimento Mensal (R$):", min_value=1000, max_value=50000, value=15000, step=1000)
            receita_projetada = modelo.predict([[novo_orcamento]])[0]
            roas_projetado = receita_projetada / novo_orcamento
            
            st.metric("🎯 Receita Prevista pela IA", f"R$ {receita_projetada:,.2f}")
            st.metric("📈 ROAS Projetado", f"{roas_projetado:.2f}x")
            
            st.info(
                f"💡 **Diagnóstico Automatizado da IA:** Para cada **R$ 1,00** adicional investido, o modelo estima um incremento de aproximadamente **R$ {modelo.coef_[0]:.2f}** em receita bruta."
            )

        with col_pred2:
            x_vals = np.linspace(X.min(), X.max() * 1.5, 100).reshape(-1, 1)
            y_vals = modelo.predict(x_vals)
            
            fig_ml = go.Figure()
            fig_ml.add_trace(go.Scatter(x=df_filtrado["Gasto_R$"], y=df_filtrado["Receita_R$"], mode='markers', name='Campanhas Reais', marker=dict(color='#38bdf8', opacity=0.7)))
            fig_ml.add_trace(go.Scatter(x=x_vals.flatten(), y=y_vals, mode='lines', name='Linha de Tendência (IA / ML)', line=dict(color='#e11d48', width=3)))
            fig_ml.update_layout(title="Dispersão Real vs. Curva Preditiva de Aprendizado de Máquina", xaxis_title="Gasto (R$)", yaxis_title="Receita (R$)")
            st.plotly_chart(fig_ml, use_container_width=True)

    st.markdown("---")
    st.subheader("📥 Exportar Relatório Executivo de BI")
    
    secoes_bi = [
        ("1. Resumo Executivo de Performance", f"<p><strong>Investimento Total:</strong> R$ {total_gasto:,.2f}<br><strong>Receita Total:</strong> R$ {total_receita:,.2f}<br><strong>Lucro Operacional:</strong> R$ {lucro_liquido:,.2f}<br><strong>ROAS Global:</strong> {roas_global:.2f}x<br><strong>CPA Médio:</strong> R$ {cpa_medio:.2f}</p>"),
        ("2. Projeção Preditiva com Machine Learning", f"<p>Simulação com aporte de <strong>R$ {novo_orcamento:,.2f}</strong> projeta faturamento de <strong>R$ {receita_projetada:,.2f}</strong> (ROAS de {roas_projetado:.2f}x).</p>"),
        ("3. Recomendações de Alocação de Verba", f"<p>Recomenda-se aumentar os aportes no canal <strong>{canal_metrics.sort_values('ROAS', ascending=False).iloc[0]['Canal']}</strong>, que apresentou o maior retorno sobre investimento.</p>")
    ]
    
    html_bi = generate_html_report(
        title="Relatório Executivo de BI & Predição de Marketing",
        subtitle="Métricas de Desempenho e Modelagem Preditiva - SENAI",
        sections=secoes_bi
    )
    
    render_download_button(
        label="📥 Baixar Relatório Executivo Completo em HTML",
        data=html_bi,
        file_name="relatorio_kpis_predicao_marketing_senai.html",
        mime="text/html"
    )

else:
    st.info("Nenhum dado disponível. Carregue uma base acima.")

render_sidebar_footer()
render_academic_footer()

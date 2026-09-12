import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.auth import check_authentication
from utils.ai_helper import render_api_key_sidebar, generate_text_ai
from utils.export_helper import generate_html_report, render_download_button
from utils.ui_components import render_sidebar_header, render_sidebar_footer, render_academic_footer

st.set_page_config(
    page_title="Matriz & Calculadora de KPIs | SENAI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_sidebar_header()
check_authentication()
render_api_key_sidebar()

st.title("📈 Matriz de KPIs & Calculadora de Métricas de Marketing")
st.caption("Alinhado aos **Módulos 2 e 6 da Ementa SENAI**: Análise de dados, definição e monitoramento de KPIs, diagnóstico de desempenho e ajustes de melhoria contínua.")

st.markdown("---")

# --- BANCO DE DADOS ESTRUTURADO DOS 18 KPIS DIDÁTICOS SENAI ---
KPIS_DATABASE = {
    # 1. TRÁFEGO & ORIGEM
    "Tráfego Orgânico": {
        "pilar": "🌐 Tráfego & Origem",
        "conceito": "Volume de usuários que chegam ao site por meio de buscas espontâneas (Google, Bing), sem custos de mídia paga.",
        "importancia": "Principal indicador de eficácia do SEO e autoridade de marca no longo prazo.",
        "formula": "Contagem total de sessões com origem orgânica no período.",
        "benchmark": "Crescimento contínuo mês a mês (Meta saudável: +5% a +15% a.m.).",
        "ferramentas": "Google Search Console, Google Analytics 4, SEMrush, Moz."
    },
    "Geração de Leads Orgânicos": {
        "pilar": "🌐 Tráfego & Origem",
        "conceito": "Visitantes que chegam via busca orgânica e realizam uma ação de cadastro (newsletter, formulário, WhatsApp, download de material).",
        "importancia": "Garante que o tráfego gerado é qualificado para se transformar em vendas futuras.",
        "formula": "Total de Cadastros / Leads gerados via Tráfego Orgânico.",
        "benchmark": "Taxa de conversão de visitante para lead entre 1,5% e 4,5%.",
        "ferramentas": "Google Analytics 4, RD Station, HubSpot, ActiveCampaign."
    },
    "Taxa de Cliques (CTR - Click-Through Rate)": {
        "pilar": "🌐 Tráfego & Origem",
        "conceito": "Percentual de usuários que visualizaram um anúncio, link ou snippet na SERP e efetivamente clicaram nele.",
        "importancia": "Mede a atratividade e relevância de títulos, meta descrições e anúncios.",
        "formula": "(Total de Cliques ÷ Total de Impressões) × 100",
        "benchmark": "Média geral: 2% a 5% em busca orgânica; > 3% em anúncios de pesquisa.",
        "ferramentas": "Google Search Console, Meta Ads Manager, Google Ads."
    },
    "Taxa de Conversão por Fonte de Tráfego": {
        "pilar": "🌐 Tráfego & Origem",
        "conceito": "Comparativo do índice de conversão segmentado por canal (Orgânico, Tráfego Pago, Redes Sociais, E-mail, Direto).",
        "importancia": "Permite identificar os canais mais rentáveis para direcionar o orçamento de marketing.",
        "formula": "(Conversões do Canal ÷ Sessões do Canal) × 100",
        "benchmark": "E-mail: 3% a 6% | Orgânico: 2% a 4% | Social Ads: 1% a 3%.",
        "ferramentas": "Google Analytics 4 (Modelos de Atribuição)."
    },
    "Taxa de Conversão por Localização Geográfica": {
        "pilar": "🌐 Tráfego & Origem",
        "conceito": "Distribuição das taxas de conversão de acordo com estados, cidades ou países dos visitantes.",
        "importancia": "Orienta campanhas geolocalizadas, logística regional e expansão de pontos de venda.",
        "formula": "(Conversões na Região ÷ Visitantes da Região) × 100",
        "benchmark": "Varia conforme frete e presença de marca na região.",
        "ferramentas": "Google Analytics 4 (Relatórios Geográficos), Meta Ads."
    },

    # 2. ENGAJAMENTO & EXPERIÊNCIA (UX)
    "Páginas por Sessão": {
        "pilar": "👥 Engajamento & Experiência (UX)",
        "conceito": "Média de páginas navegadas por um usuário durante uma visita única ao site.",
        "importancia": "Indica o valor percebido do conteúdo e a fluidez da arquitetura de navegação.",
        "formula": "Total de Visualizações de Página ÷ Total de Sessões",
        "benchmark": "Ideal: 2.5 a 4.5 páginas por sessão (e-commerces e portais de conteúdo).",
        "ferramentas": "Google Analytics 4."
    },
    "Duração Média da Sessão": {
        "pilar": "👥 Engajamento & Experiência (UX)",
        "conceito": "Tempo médio que os usuários permanecem ativos no site durante suas visitas.",
        "importancia": "Reflete a capacidade do conteúdo de reter a atenção e estimular a leitura detalhada.",
        "formula": "Tempo Total de Todas as Sessões ÷ Total de Sessões",
        "benchmark": "1 minuto e 30 segundos a 3 minutos e 30 segundos.",
        "ferramentas": "Google Analytics 4, Hotjar."
    },
    "Tempo Médio na Página": {
        "pilar": "👥 Engajamento & Experiência (UX)",
        "conceito": "Tempo gasto especificamente em uma URL ou página de destino individual.",
        "importancia": "Ajuda a diferenciar artigos de alta leitura de páginas de rápida consulta ou saída.",
        "formula": "Tempo Total Gasto na Página ÷ Visualizações da Página",
        "benchmark": "Artigos de blog: > 2 min | Landing Pages de captura: 45s a 1m30s.",
        "ferramentas": "Google Analytics 4."
    },
    "Tempo de Carregamento da Página (Page Speed)": {
        "pilar": "👥 Engajamento & Experiência (UX)",
        "conceito": "Tempo em segundos necessário para o navegador baixar e renderizar todos os elementos da página.",
        "importancia": "2 segundos de atraso podem dobrar a taxa de rejeição; cada 100ms a mais reduz conversões em até 7%.",
        "formula": "Medição de TTFB (Time to First Byte) + LCP (Largest Contentful Paint).",
        "benchmark": "Excelente: < 1.8 segundos | Regular: 1.8s a 3.0s | Crítico: > 3.0s.",
        "ferramentas": "Google PageSpeed Insights, GTmetrix, Lighthouse."
    },
    "Taxa de Cliques em Elementos Interativos": {
        "pilar": "👥 Engajamento & Experiência (UX)",
        "conceito": "Percentual de visitantes que clicam em carrosséis, vídeos, calculadoras, abas ou filtros de produtos.",
        "importancia": "Mede a eficácia dos recursos interativos na retenção e condução do usuário.",
        "formula": "(Sessões com Interação no Elemento ÷ Total de Sessões) × 100",
        "benchmark": "Varia de 15% a 40% dependendo do elemento e destaque.",
        "ferramentas": "Google Tag Manager + GA4 (Event Tracking), Hotjar, Microsoft Clarity."
    },

    # 3. RETENÇÃO & PONTOS DE FRICÇÃO
    "Taxa de Rejeição (Bounce Rate)": {
        "pilar": "⚠️ Retenção & Fricção",
        "conceito": "Percentual de sessões em que o usuário acessou apenas uma página e saiu sem realizar nenhuma ação ou evento de engajamento.",
        "importancia": "Sinaliza se a página entrega imediatamente o que o usuário procurava na busca.",
        "formula": "(Sessões Não Engajadas ÷ Total de Sessões) × 100",
        "benchmark": "Excelente: < 35% | Médio: 40% a 55% | Alerta: > 65% (para páginas comerciais).",
        "ferramentas": "Google Analytics 4."
    },
    "Taxa de Rejeição por Página": {
        "pilar": "⚠️ Retenção & Fricção",
        "conceito": "Mapeamento granular do índice de abandono imediato por página individual do site.",
        "importancia": "Permite identificar páginas problemáticas específicas que necessitam de redesign ou ajuste de conteúdo.",
        "formula": "(Rejeições da Página Específica ÷ Entradas na Página) × 100",
        "benchmark": "Páginas de blog costumam ter rejeição maior que páginas de produto.",
        "ferramentas": "Google Analytics 4."
    },
    "Taxa de Rejeição por Dispositivo": {
        "pilar": "⚠️ Retenção & Fricção",
        "conceito": "Comparativo da taxa de rejeição entre Mobile (smartphones) e Desktop (computadores).",
        "importancia": "Se o mobile tiver rejeição muito mais alta, indica que o site não é responsivo ou demora para carregar.",
        "formula": "(Rejeições em Mobile ÷ Sessões Mobile) vs. (Rejeições em Desktop ÷ Sessões Desktop)",
        "benchmark": "Diferença máxima aceitável entre Mobile e Desktop: 10 pontos percentuais.",
        "ferramentas": "Google Analytics 4."
    },
    "Taxa de Saída (Exit Rate)": {
        "pilar": "⚠️ Retenção & Fricção",
        "conceito": "Percentual de visualizações em que uma página específica foi a última da visita do usuário.",
        "importancia": "Mapeia os pontos de fuga do funil de vendas (ex: desistência na tela de frete ou pagamento).",
        "formula": "(Total de Saídas da Página ÷ Total de Visualizações da Página) × 100",
        "benchmark": "Páginas de 'Obrigado pela compra' devem ter alta saída; carrinhos devem ter baixa saída.",
        "ferramentas": "Google Analytics 4."
    },

    # 4. CONVERSÃO & VALOR DO NEGÓCIO
    "Taxa de Conversão (CVR)": {
        "pilar": "💰 Conversão & Negócio",
        "conceito": "Percentual de visitantes que completaram com sucesso o objetivo principal de negócio da página.",
        "importancia": "Principal métrica de retorno sobre o investimento (ROI) de todo o esforço de marketing.",
        "formula": "(Total de Conversões / Vendas ÷ Total de Visitantes Únicos) × 100",
        "benchmark": "E-commerce no Brasil: 1,2% a 2,5% | Serviços/B2B: 2,5% a 7,0%.",
        "ferramentas": "Google Analytics 4, Plataforma de E-commerce, CRM."
    },
    "Taxa de Conversão por Dispositivo": {
        "pilar": "💰 Conversão & Negócio",
        "conceito": "Avaliação do percentual de fechamento de negócios segmentado por celulares, tablets e desktops.",
        "importancia": "Revela se o processo de checkout e preenchimento de dados é simples no celular.",
        "formula": "(Conversões no Dispositivo ÷ Visitantes no Dispositivo) × 100",
        "benchmark": "Desktop tradicionalmente tem taxa maior, mas o Mobile deve representar o maior volume de vendas.",
        "ferramentas": "Google Analytics 4."
    },
    "Taxa de Retenção de Usuários": {
        "pilar": "💰 Conversão & Negócio",
        "conceito": "Percentual de clientes ou visitantes que retornam para interagir ou comprar novamente no período.",
        "importancia": "Retener clientes existentes custa até 5x a 7x menos do que adquirir novos clientes (CAC).",
        "formula": "(Clientes Ativos no Fim do Período - Novos Clientes) ÷ Clientes no Início do Período × 100",
        "benchmark": "SaaS / Assinaturas: > 85% anual | E-commerce: > 25% a 35% de recompra.",
        "ferramentas": "CRM, Plataforma de Vendas, ERP."
    },
    "Valor do Tempo de Vida do Cliente (LTV - Lifetime Value)": {
        "pilar": "💰 Conversão & Negócio",
        "conceito": "Faturamento líquido total estimado que um cliente traz para a empresa durante todo o tempo em que permanece comprando.",
        "importancia": "Define o teto máximo que sua empresa pode investir para adquirir cada cliente (relação LTV/CAC > 3x).",
        "formula": "Ticket Médio × Média de Compras por Ano × Tempo Médio de Retenção (anos)",
        "benchmark": "A relação ideal de sustentabilidade é: LTV ≥ 3 × CAC (Custo de Aquisição).",
        "ferramentas": "CRM, ERP, Google Analytics 4."
    }
}

tab_dict, tab_calc, tab_ai, tab_export = st.tabs([
    "📚 Dicionário Didático dos 18 KPIs",
    "🧮 Calculadora & Simulador Prático",
    "🤖 Gerador de Metas SMART com IA",
    "📥 Exportar Dicionário & Planejamento"
])

# ==============================================================================
# ABA 1: DICIONÁRIO E MATRIZ ESTRATÉGICA DOS 18 KPIS
# ==============================================================================
with tab_dict:
    st.subheader("📚 Matriz Completa de Indicadores de Desempenho (KPIs)")
    st.write("Filtre os KPIs pelo pilar estratégico para compreender o conceito, fórmula, ferramentas e benchmarks recomendados:")
    
    col_filtro, _ = st.columns([1, 2])
    with col_filtro:
        pilares_lista = ["Todos os Pilares", "🌐 Tráfego & Origem", "👥 Engajamento & Experiência (UX)", "⚠️ Retenção & Fricção", "💰 Conversão & Negócio"]
        filtro_pilar = st.selectbox("Selecione o Pilar de Marketing:", pilares_lista)
        
    for kpi_nome, kpi_info in KPIS_DATABASE.items():
        if filtro_pilar == "Todos os Pilares" or kpi_info["pilar"] == filtro_pilar:
            with st.expander(f"{kpi_info['pilar']} • **{kpi_nome}**"):
                c1, c2 = st.columns([1.2, 1])
                with c1:
                    st.markdown(f"**📖 O que é:** {kpi_info['conceito']}")
                    st.markdown(f"**🎯 Importância no Marketing:** {kpi_info['importancia']}")
                    st.markdown(f"**📐 Fórmula de Cálculo:** `{kpi_info['formula']}`")
                with c2:
                    st.info(f"**📊 Benchmark Recomendado:**\n{kpi_info['benchmark']}")
                    st.caption(f"🛠️ **Ferramentas de Medição:** {kpi_info['ferramentas']}")

# ==============================================================================
# ABA 2: CALCULADORA & SIMULADOR PRÁTICO DE KPIS
# ==============================================================================
with tab_calc:
    st.subheader("🧮 Calculadora Interativa de Métricas de Marketing")
    st.write("Insira os números simulados da sua campanha ou site para calcular o KPI instantaneamente e obter o diagnóstico:")
    
    col_sel, col_inputs = st.columns([1, 2], gap="large")
    
    with col_sel:
        kpi_escolhido = st.selectbox("Selecione a Métrica para Simular:", [
            "Taxa de Conversão (CVR)",
            "Taxa de Cliques (CTR)",
            "Taxa de Rejeição (Bounce Rate)",
            "Páginas por Sessão",
            "Valor do Tempo de Vida (LTV)",
            "Relação LTV / CAC"
        ])
        
    with col_inputs:
        if kpi_escolhido == "Taxa de Conversão (CVR)":
            st.markdown("#### Simulação: Taxa de Conversão (CVR)")
            c_vis = st.number_input("Total de Visitantes Únicos no Mês:", min_value=10, value=5000, step=500)
            c_conv = st.number_input("Total de Conversões / Vendas Realizadas:", min_value=0, value=120, step=10)
            
            cvr_calc = (c_conv / c_vis * 100) if c_vis > 0 else 0
            
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Taxa de Conversão (CVR)", f"{cvr_calc:.2f}%")
            if cvr_calc >= 2.0:
                col_m2.success("🟢 **Desempenho Saudável:** Acima da média nacional de e-commerce (2.0%).")
            elif cvr_calc >= 1.0:
                col_m2.warning("🟡 **Desempenho Mediano:** Potencial de melhoria com testes A/B em landing pages.")
            else:
                col_m2.error("🔴 **Atenção:** Taxa baixa. Verifique usabilidade, proposta de valor e clareza da oferta.")
                
        elif kpi_escolhido == "Taxa de Cliques (CTR)":
            st.markdown("#### Simulação: Taxa de Cliques (CTR)")
            c_imp = st.number_input("Total de Impressões (Visualizações do Anúncio/Snippet):", min_value=100, value=25000, step=1000)
            c_cliques = st.number_input("Total de Cliques Efetivos:", min_value=0, value=750, step=50)
            
            ctr_calc = (c_cliques / c_imp * 100) if c_imp > 0 else 0
            
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("CTR Calculado", f"{ctr_calc:.2f}%")
            if ctr_calc >= 3.0:
                col_m2.success("🟢 **Excelente CTR:** O título e a chamada (CTA) geram alto interesse.")
            elif ctr_calc >= 1.5:
                col_m2.warning("🟡 **CTR Regular:** Teste variações de headlines e gatilhos de curiosidade/benefício.")
            else:
                col_m2.error("🔴 **CTR Baixo:** Revise o criativo e o alinhamento da palavra-chave com o público.")

        elif kpi_escolhido == "Taxa de Rejeição (Bounce Rate)":
            st.markdown("#### Simulação: Taxa de Rejeição (Bounce Rate)")
            c_tot_sess = st.number_input("Total de Sessões:", min_value=10, value=8000, step=500)
            c_nao_eng = st.number_input("Sessões Não Engajadas (Saída sem interação):", min_value=0, value=3200, step=200)
            
            bounce_calc = (c_nao_eng / c_tot_sess * 100) if c_tot_sess > 0 else 0
            
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Taxa de Rejeição", f"{bounce_calc:.1f}%")
            if bounce_calc <= 45.0:
                col_m2.success("🟢 **Ótima Retenção:** Visitantes encontram valor e continuam navegando.")
            elif bounce_calc <= 65.0:
                col_m2.warning("🟡 **Rejeição Mediana:** Verifique tempo de carregamento e correspondência com a busca.")
            else:
                col_m2.error("🔴 **Rejeição Alta:** Provável lentidão no site ou conteúdo desalinhado com o anúncio.")

        elif kpi_escolhido == "Páginas por Sessão":
            st.markdown("#### Simulação: Páginas por Sessão")
            s_sess = st.number_input("Total de Sessões no Período:", min_value=10, value=4000, step=500)
            s_views = st.number_input("Total de Páginas Vistas (Pageviews):", min_value=10, value=12800, step=1000)
            
            pps_calc = (s_views / s_sess) if s_sess > 0 else 0
            
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Páginas / Sessão", f"{pps_calc:.2f}")
            if pps_calc >= 3.0:
                col_m2.success("🟢 **Excelente Profundidade:** Navegação fluida com bom link building interno.")
            else:
                col_m2.warning("🟡 **Atenção:** Estimule links recomendados, produtos relacionados e carrosséis.")

        elif kpi_escolhido == "Valor do Tempo de Vida (LTV)":
            st.markdown("#### Simulação: Lifetime Value (LTV)")
            ltv_ticket = st.number_input("Ticket Médio por Compra (R$):", min_value=10.0, value=180.0, step=10.0)
            ltv_freq = st.number_input("Frequência Média de Compras por Ano (por cliente):", min_value=1.0, value=3.5, step=0.5)
            ltv_anos = st.number_input("Tempo Médio de Retenção do Cliente (em Anos):", min_value=0.5, value=2.5, step=0.5)
            
            ltv_calc = ltv_ticket * ltv_freq * ltv_anos
            
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("LTV por Cliente", f"R$ {ltv_calc:,.2f}")
            col_m2.info(f"💡 Em média, cada novo cliente conquistado gerará **R$ {ltv_calc:,.2f}** em receita bruta ao longo do relacionamento.")

        elif kpi_escolhido == "Relação LTV / CAC":
            st.markdown("#### Simulação: Relação LTV / CAC (Sustentabilidade)")
            ltv_val = st.number_input("Valor do LTV do Cliente (R$):", min_value=10.0, value=1575.0, step=50.0)
            cac_val = st.number_input("Custo de Aquisição de Cliente - CAC (R$):", min_value=10.0, value=350.0, step=25.0)
            
            ratio = (ltv_val / cac_val) if cac_val > 0 else 0
            
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Relação LTV / CAC", f"{ratio:.2f}x")
            if ratio >= 3.0:
                col_m2.success(f"🟢 **Modelo de Negócio Altamente Escalável:** LTV é mais de {ratio:.1f}x o custo de aquisição.")
            elif ratio >= 1.5:
                col_m2.warning("🟡 **Atenção:** Margem apertada. Reduza o CAC ou aumente a retenção/cross-sell.")
            else:
                col_m2.error("🔴 **Inviável no Longo Prazo:** O custo para adquirir o cliente consome quase todo o lucro gerado.")

# ==============================================================================
# ABA 3: GERADOR DE METAS SMART COM IA
# ==============================================================================
with tab_ai:
    st.subheader("🤖 Planejamento de Metas SMART com Inteligência Artificial")
    st.write("A IA estrutura um plano de metas acionável para o seu projeto de marketing com base nos KPIs escolhidos:")
    
    c_empresa = st.text_input("Segmento da Empresa / Negócio:", value="Escola de Cursos Profissionalizantes de Tecnologia")
    c_foco = st.multiselect("Selecione os 3 KPIs Prioritários para Otimizar:", list(KPIS_DATABASE.keys()), default=["Tráfego Orgânico", "Geração de Leads Orgânicos", "Taxa de Conversão (CVR)"])
    c_desafio = st.text_area("Desafio Atual do Negócio:", value="O site recebe visitantes, mas a taxa de conversão em matrículas está abaixo de 1% e o tráfego mobile tem alta rejeição.")
    
    if st.button("🚀 Gerar Estratégia de Metas SMART com IA", type="primary", use_container_width=True):
        prompt_smart = f"""
        Você é um consultor sênior de Marketing Digital do SENAI especialista em métricas de performance e BI.
        Crie um plano estratégico de METAS SMART para o seguinte negócio:
        - Segmento: {c_empresa}
        - KPIs Escolhidos: {', '.join(c_foco)}
        - Desafio Atual: {c_desafio}
        
        Estruture a resposta em Markdown contendo:
        1. Definição de Meta SMART (Específica, Mensurável, Atingível, Relevante e Temporal) para cada KPI selecionado.
        2. 3 Ações Práticas Imediatas de Growth Marketing para atingir essas metas em 90 dias.
        3. Frequência recomendada de monitoramento (Semanal vs Mensal) para cada métrica.
        """
        
        with st.spinner("Estruturando plano estratégico com IA..."):
            plano_smart_ia = generate_text_ai(prompt_smart, "Você é um consultor de métricas do SENAI.")
            
            if not plano_smart_ia:
                plano_smart_ia = f"""### 🎯 Plano Estratégico de Metas SMART • {c_empresa}

**1. Metas SMART para os KPIs Selecionados:**
- **{c_foco[0] if len(c_foco)>0 else 'Tráfego Orgânico'}:** Aumentar em **25%** o tráfego orgânico nos próximos 90 dias através da publicação de 8 artigos de blog otimizados para termos de busca transacionais.
- **{c_foco[1] if len(c_foco)>1 else 'Leads Orgânicos'}:** Elevar a captura de leads orgânicos de 50 para **120 leads/mês** até o fim do trimestre implementando um novo formulário simplificado com CTA de alta visibilidade.
- **{c_foco[2] if len(c_foco)>2 else 'Taxa de Conversão'}:** Subir a taxa de conversão média (CVR) de 0.9% para **2.2%** em 60 dias por meio de otimização mobile e testes A/B na página de inscrições.

**2. Plano de Ação em 90 Dias:**
1. **Otimização Mobile-First:** Reduzir o tempo de carregamento no celular para menos de 2.0 segundos para conter a taxa de rejeição.
2. **Copywriting Orientado à Ação:** Implementar gatilhos de prova social e escassez de vagas na página principal.
3. **Automação de Nutrição:** Configurar disparos automáticos via WhatsApp/E-mail nos primeiros 5 minutos após o preenchimento do formulário.
"""
            st.markdown(plano_smart_ia)

# ==============================================================================
# ABA 4: EXPORTAR DICIONÁRIO & PLANEJAMENTO EM HTML
# ==============================================================================
with tab_export:
    st.subheader("📥 Leve o Guia Completo de KPIs para Casa")
    st.write("Baixe o documento interativo com todas as 18 definições, fórmulas matemáticas e benchmarks prontos para consulta:")
    
    kpis_html = "<div style='display: grid; grid-template-columns: 1fr 1fr; gap: 16px;'>"
    for k_nome, k_info in KPIS_DATABASE.items():
        kpis_html += f"""
        <div style='background: #1e293b; border: 1px solid #334155; padding: 14px; border-radius: 8px;'>
            <span style='background: #38bdf8; color: #0f172a; font-size: 0.75rem; font-weight: bold; padding: 2px 8px; border-radius: 12px;'>{k_info['pilar']}</span>
            <h3 style='color: #ffffff; margin: 8px 0 4px 0;'>{k_nome}</h3>
            <p style='color: #cbd5e1; font-size: 0.9rem; margin-bottom: 6px;'>{k_info['conceito']}</p>
            <p style='color: #94a3b8; font-size: 0.85rem; margin: 0;'><strong>Fórmula:</strong> <code>{k_info['formula']}</code></p>
            <p style='color: #fbbf24; font-size: 0.85rem; margin: 4px 0 0 0;'><strong>Benchmark:</strong> {k_info['benchmark']}</p>
        </div>
        """
    kpis_html += "</div>"
    
    secoes_guia_kpi = [
        ("1. Matriz Didática dos 18 KPIs de Marketing Digital", kpis_html),
        ("2. Guia de Implementação e Boas Práticas", "<p>Recomenda-se realizar o acompanhamento semanal dos KPIs de Tráfego e Rejeição, e o monitoramento mensal dos KPIs de Conversão, LTV e CAC em reuniões de alinhamento tático.</p>")
    ]
    
    html_kpi_doc = generate_html_report(
        title="Guia Executivo & Dicionário de KPIs de Marketing Digital",
        subtitle="Matriz Completa de Indicadores, Fórmulas e Benchmarks — SENAI-SP",
        sections=secoes_guia_kpi
    )
    
    render_download_button(
        label="📥 Baixar Dicionário & Matriz de KPIs em HTML",
        data=html_kpi_doc,
        file_name="guia_kpis_marketing_digital_senai.html",
        mime="text/html"
    )

render_sidebar_footer()
render_academic_footer()

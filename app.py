import sys
import os

# Garante que a raiz do projeto esteja no sys.path do Streamlit Cloud
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from utils.auth import check_authentication
from utils.ai_helper import render_api_key_sidebar
from utils.ui_components import render_sidebar_header, render_sidebar_footer, render_academic_footer

# Configuração da página principal
st.set_page_config(
    page_title="Marketing AI Lab | SENAI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Renderiza cabeçalho e rodapé da barra lateral
render_sidebar_header()

# Validação da senha da turma
check_authentication()

# Configuração opcional de chave de IA na barra lateral
render_api_key_sidebar()

# CSS Customizado para identidade visual limpa e badges estilizadas
st.markdown(
    """
    <style>
    .badge-code {
        background-color: #1e293b;
        color: #38bdf8;
        border: 1px solid #334155;
        padding: 2px 7px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.85rem;
    }
    .competency-item {
        margin-bottom: 0.9rem;
        line-height: 1.6;
        font-size: 1rem;
        color: #cbd5e1;
    }
    .competency-item strong {
        color: #f8fafc;
    }
    .feature-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1.25rem;
        height: 100%;
        transition: transform 0.2s, border-color 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-3px);
        border-color: #38bdf8;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Cabeçalho Principal (Estilo Acadêmico / MIT Open Source)
st.markdown("# Bem-vindo ao Marketing AI Lab 🚀")
st.markdown("### Laboratório Prático de Inteligência Artificial para Marketing Digital")

# Banner / Caixa Informativa
st.info(
    "Este aplicativo é um laboratório integrador educacional de código aberto (MIT) estruturado na sequência exata da ementa do curso **Aperfeiçoamento Profissional em Marketing Digital com Inteligência Artificial (30h)** do SENAI-SP."
)

st.write("")

# Seção de Competências e Tecnologias
st.markdown("### 📚 Competências e Tecnologias Desenvolvidas:")

st.markdown(
    """
    <div style="margin-top: 1rem; margin-bottom: 1.5rem;">
        <div class="competency-item">
            • <strong>1. SEO Técnico, GEO (IA Search) & Pesquisa de Palavras-Chave:</strong> Auditoria on-page de tags, GEO Readiness para ChatGPT/Perplexity/Gemini, bots de IA no robots.txt, Schema LocalBusiness, geomarketing e matriz de cauda longa <span class="badge-code">SEO</span> <span class="badge-code">GEO-AI</span> <span class="badge-code">Keywords-LongTail</span> <span class="badge-code">Geomarketing</span>.
        </div>
        <div class="competency-item">
            • <strong>2. Agentes Conversacionais & Atendimento Inteligente:</strong> Assistentes virtuais 24/7 com extração contextual de intenções, tratamento empático de objeções e termômetro de <em>Lead Scoring</em> dinâmico <span class="badge-code">Conversational-AI</span> <span class="badge-code">Lead-Scoring</span> <span class="badge-code">NLP</span>.
        </div>
        <div class="competency-item">
            • <strong>3. Matriz de Métricas & Engenharia de KPIs:</strong> Dicionário didático dos 18 KPIs fundamentais de marketing, simulador interativo de fórmulas e gerador de metas SMART com IA <span class="badge-code">Marketing-KPIs</span> <span class="badge-code">Growth-Metrics</span> <span class="badge-code">BI</span>.
        </div>
        <div class="competency-item">
            • <strong>4. Publicidade Programática & Mídia Preditiva:</strong> Simulação de leilão em tempo real (RTB), estratégias de <em>Smart Bidding</em> (IA) vs. Lance Manual e análise de funil de conversão <span class="badge-code">RTB-Engine</span> <span class="badge-code">Smart-Bidding</span> <span class="badge-code">AdTech</span>.
        </div>
        <div class="competency-item">
            • <strong>5. Sistemas de Recomendação & Neuromarketing:</strong> Algoritmos de Filtragem Baseada em Conteúdo e Filtragem Colaborativa integrados a gatilhos cognitivos de conversão em e-commerce <span class="badge-code">Recommender-Systems</span> <span class="badge-code">Collaborative-Filtering</span> <span class="badge-code">Neuromarketing</span>.
        </div>
        <div class="competency-item">
            • <strong>6. Processamento de Linguagem Natural & Copywriting com IA:</strong> Geração de copies estruturadas com frameworks AIDA e PAS, engenharia de prompts para criativos visuais e auditoria de conformidade ética/LGPD <span class="badge-code">Copywriting</span> <span class="badge-code">Prompt-Engineering</span> <span class="badge-code">LGPD-Ethics</span>.
        </div>
        <div class="competency-item">
            • <strong>7. Machine Learning Supervisionado & Análise Preditiva:</strong> Previsão de tendências de faturamento, análise de CAC, LTV e ROAS com regressão linear <span class="badge-code">Scikit-Learn</span> <span class="badge-code">Pandas</span> <span class="badge-code">Plotly</span> <span class="badge-code">Predictive-AI</span>.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# Módulos Práticos do Curso na Sequência Exata da Ementa SENAI
st.markdown("### 🗺️ Módulos Práticos do Curso (Sequência Pedagógica SENAI):")
st.write("Navegue pelos laboratórios utilizando o menu lateral ou os atalhos abaixo:")

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown(
        """
        <div class="feature-card">
            <h4>🔍 1. Auditoria SEO, GEO & Palavras-Chave</h4>
            <p style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 8px;">Módulo 1 da Ementa: SEO On-Page, GEO para IA (ChatGPT/Perplexity), Schema LocalBusiness e Matriz de Cauda Longa.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Abrir Auditoria de SEO & GEO ➡️", key="btn_nav_m1", use_container_width=True):
        st.switch_page("pages/1_🔍_Auditoria_SEO_e_Palavras_Chave.py")

with row1_col2:
    st.markdown(
        """
        <div class="feature-card">
            <h4>🤖 2. Construtor de Chatbot & Qualificação de Leads</h4>
            <p style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 8px;">Módulo 1 da Ementa: Automação 24/7, Tratamento de Objeções e Lead Scoring Dinâmico.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Abrir Construtor de Chatbot ➡️", key="btn_nav_m2", use_container_width=True):
        st.switch_page("pages/2_🤖_Chatbot_e_Atendimento.py")

st.write("")
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown(
        """
        <div class="feature-card">
            <h4>📈 3. Matriz de KPIs & Calculadora de Métricas</h4>
            <p style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 8px;">Módulo 2 da Ementa: Dicionário dos 18 KPIs, Calculadora com Diagnósticos e Metas SMART com IA.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Abrir Matriz de KPIs ➡️", key="btn_nav_m3", use_container_width=True):
        st.switch_page("pages/3_📈_Matriz_e_Calculadora_de_KPIs.py")

with row2_col2:
    st.markdown(
        """
        <div class="feature-card">
            <h4>🎯 4. Simulador de Mídia Programática & RTB</h4>
            <p style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 8px;">Módulo 3 da Ementa: Leilão em tempo real, Smart Bidding vs Manual e ROAS.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Abrir Simulador de Programática ➡️", key="btn_nav_m4", use_container_width=True):
        st.switch_page("pages/4_🎯_Simulador_Programatica.py")

st.write("")
row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    st.markdown(
        """
        <div class="feature-card">
            <h4>🛍️ 5. Recomendação, Neuromarketing & UX</h4>
            <p style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 8px;">Módulo 4 da Ementa: Filtragem Colaborativa/Conteúdo e 4 Gatilhos Mentais Cognitivos.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Abrir Motor de Recomendação ➡️", key="btn_nav_m5", use_container_width=True):
        st.switch_page("pages/5_🛍️_Recomendacao_e_UX.py")

with row3_col2:
    st.markdown(
        """
        <div class="feature-card">
            <h4>✍️ 6. Copywriting, Criativos & Ética com IA</h4>
            <p style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 8px;">Módulo 5 da Ementa: Frameworks AIDA/PAS, Prompts de Imagem e Auditoria Ética/LGPD.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Abrir Estúdio de Copywriting ➡️", key="btn_nav_m6", use_container_width=True):
        st.switch_page("pages/6_✍️_Copy_e_Criacao_IA.py")

st.write("")
row4_col1, row4_col2 = st.columns(2)

with row4_col1:
    st.markdown(
        """
        <div class="feature-card">
            <h4>📊 7. Dashboard de BI & Previsão Preditiva (ML)</h4>
            <p style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 8px;">Módulo 6 da Ementa: Análise de Dados e Projeção de Vendas com Machine Learning Supervisionado.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Abrir Dashboard Preditivo ➡️", key="btn_nav_m7", use_container_width=True):
        st.switch_page("pages/7_📊_Dashboard_KPIs_Preditivo.py")

with row4_col2:
    st.markdown(
        """
        <div class="feature-card">
            <h4>🌐 8. Biblioteca de Ferramentas, Buscas & Hub de IA</h4>
            <p style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 8px;">Hub Integrado: Multibusca em 1-clique, Ferramentas Google, Motores GEO, SEO e Inteligência Competitiva.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Abrir Biblioteca & Hub de Buscas ➡️", key="btn_nav_m8", use_container_width=True):
        st.switch_page("pages/8_🌐_Hub_de_Ferramentas_e_Buscas.py")

# Rodapé da Barra Lateral
render_sidebar_footer()

# Rodapé Acadêmico e Disclaimer MIT no final da página
render_academic_footer()

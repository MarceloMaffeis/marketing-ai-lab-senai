import streamlit as st
from utils.auth import check_authentication
from utils.ai_helper import render_api_key_sidebar

# Configuração da página principal
st.set_page_config(
    page_title="Marketing AI Lab | SENAI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Validação da senha da turma
check_authentication()

# Configuração opcional de chave de IA na barra lateral
render_api_key_sidebar()

# CSS Customizado para deixar o app com visual premium
st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #311042 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .badge-senai {
        display: inline-block;
        background-color: #e11d48;
        color: white;
        font-weight: 700;
        font-size: 0.8rem;
        padding: 4px 12px;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
    }
    .feature-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        height: 100%;
        transition: transform 0.2s, border-color 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-4px);
        border-color: #38bdf8;
    }
    .metric-box {
        background-color: #0f172a;
        border-left: 4px solid #38bdf8;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header Principal
st.markdown(
    """
    <div class="main-header">
        <span class="badge-senai">SENAI-SP • Gestão & Negócios</span>
        <h1 class="main-title">Marketing AI Lab</h1>
        <p style="font-size: 1.15rem; color: #cbd5e1; margin-top: 8px;">
            Ambiente prático e interativo para o curso de <strong>Aperfeiçoamento Profissional em Marketing Digital com Inteligência Artificial (30h)</strong>.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Destaques e Métricas do Curso
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="⏱️ Carga Horária", value="30 Horas")
with col2:
    st.metric(label="🧠 Capacidades Técnicas", value="6 Pilares")
with col3:
    st.metric(label="🛠️ Ferramentas Práticas", value="5 Módulos")
with col4:
    st.metric(label="📈 Metodologia", value="100% Hands-on")

st.markdown("---")

st.subheader("🗺️ Módulos & Laboratórios Práticos Disponíveis")
st.write("Selecione um dos módulos no menu lateral ou explore as ferramentas abaixo:")

# Grid com os 5 módulos interativos
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown(
        """
        <div class="feature-card">
            <h3>✍️ 1. Copywriting & Conteúdo com IA</h3>
            <p style="color: #94a3b8;"><strong>Módulo 5 da Ementa:</strong> Criação de Conteúdo, Copywriting & Ética.</p>
            <div class="metric-box">
                • Geração com frameworks <strong>AIDA</strong> e <strong>PAS</strong><br>
                • Engenharia de Prompts para criativos visuais<br>
                • Verificador de conformidade ética e LGPD
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Abrir Estúdio de Copywriting ➡️", key="btn_m1", use_container_width=True):
        st.switch_page("pages/1_✍️_Copy_e_Criacao_IA.py")

with row1_col2:
    st.markdown(
        """
        <div class="feature-card">
            <h3>🎯 2. Simulador de Mídia Programática & RTB</h3>
            <p style="color: #94a3b8;"><strong>Módulo 3 da Ementa:</strong> Publicidade Programática e Algoritmos de Lance.</p>
            <div class="metric-box">
                • Simulação de leilão em tempo real (RTB)<br>
                • Comparativo: Lance Manual vs. <strong>Smart Bidding (IA)</strong><br>
                • Métricas em tempo real: CPM, CTR, CPA e ROAS
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Abrir Simulador de Mídia ➡️", key="btn_m2", use_container_width=True):
        st.switch_page("pages/2_🎯_Simulador_Programatica.py")

st.write("")
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown(
        """
        <div class="feature-card">
            <h3>🛍️ 3. Recomendação & Neuromarketing</h3>
            <p style="color: #94a3b8;"><strong>Módulo 4 da Ementa:</strong> Experiência do Cliente e Personalização.</p>
            <div class="metric-box">
                • Vitrine inteligente com Filtragem Baseada em Conteúdo e Colaborativa<br>
                • Laboratório de <strong>Gatilhos de Neuromarketing</strong> (Urgência, Escassez)<br>
                • Impacto na taxa de conversão do e-commerce
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Abrir Motor de Recomendação ➡️", key="btn_m3", use_container_width=True):
        st.switch_page("pages/3_🛍️_Recomendacao_e_UX.py")

with row2_col2:
    st.markdown(
        """
        <div class="feature-card">
            <h3>📊 4. Dashboard de KPIs & Machine Learning</h3>
            <p style="color: #94a3b8;"><strong>Módulos 2 e 6 da Ementa:</strong> Análise de Dados e Métricas de Marketing.</p>
            <div class="metric-box">
                • Análise de campanhas (Meta Ads, Google, TikTok, RTB)<br>
                • Projeção preditiva de vendas com Regressão Linear/ML<br>
                • Diagnóstico automático de ROI, CAC e LTV
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Abrir Dashboard Preditivo ➡️", key="btn_m4", use_container_width=True):
        st.switch_page("pages/4_📊_Dashboard_KPIs_Preditivo.py")

st.write("")
row3_col1, _ = st.columns([1, 1])
with row3_col1:
    st.markdown(
        """
        <div class="feature-card">
            <h3>🤖 5. Construtor de Chatbot & Qualificação de Leads</h3>
            <p style="color: #94a3b8;"><strong>Módulo 1 da Ementa:</strong> Automação, Chatbots e Assistentes Virtuais.</p>
            <div class="metric-box">
                • Criação de personas e regras de atendimento 24/7<br>
                • Simulador de chat interativo em tempo real<br>
                • Algoritmo de Lead Scoring (Quente, Morno, Frio)
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Abrir Construtor de Chatbot ➡️", key="btn_m5", use_container_width=True):
        st.switch_page("pages/5_🤖_Chatbot_e_Atendimento.py")

st.markdown("---")

# Guia para os alunos levarem os resultados para casa
with st.expander("📥 Como os alunos salvam e levam seus projetos para casa?"):
    st.markdown(
        """
        1. **Relatórios em HTML / PDF:** Em cada ferramenta, há um botão para gerar um relatório completo da sua atividade prática.
        2. **Cópias de Textos e Prompts:** Você pode copiar os textos gerados pela IA com 1 clique e colá-los no seu Canva, Meta Ads Manager ou gerenciador de postagens.
        3. **Acesso Permanente:** Este link continuará disponível para você consultar seus dados e testar novas campanhas sempre que precisar!
        """
    )

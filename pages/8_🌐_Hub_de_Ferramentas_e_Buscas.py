import sys
import os
import urllib.parse

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from utils.auth import check_authentication
from utils.ai_helper import render_api_key_sidebar
from utils.ui_components import render_sidebar_header, render_sidebar_footer, render_academic_footer

st.set_page_config(page_title="Biblioteca & Hub de Ferramentas | SENAI", page_icon="🌐", layout="wide")
render_sidebar_header()
check_authentication()
render_api_key_sidebar()

st.title("🌐 Biblioteca de Ferramentas, Buscas & Hub de IA")
st.caption("Alinhado ao curso de **Marketing Digital com Inteligência Artificial (30h) do SENAI-SP**: Hub centralizado de ferramentas oficiais do Google, motores de busca com IA (GEO), utilitários de SEO, inteligência competitiva e análise de dados.")

# -------------------------------------------------------------
# BARRA DE MULTIBUSCA INTELIGENTE (1-CLIQUE PARA MÚLTIPLAS FERRAMENTAS)
# -------------------------------------------------------------
st.markdown("""
<div style='background: linear-gradient(135deg, #1e293b, #0f172a); border: 1px solid #3b82f6; border-radius: 12px; padding: 20px; margin-bottom: 25px;'>
    <h3 style='color: #60a5fa; margin-top: 0;'>🔍 Lançador Rápido de Multibusca & Diagnóstico</h3>
    <p style='color: #cbd5e1; font-size: 0.95rem; margin-bottom: 15px;'>
        Digite uma <strong>palavra-chave, nicho ou endereço de site</strong> para abrir a análise em tempo real nas ferramentas oficiais do Google e nos motores de busca com IA.
    </p>
</div>
""", unsafe_allow_html=True)

col_search_kw, col_search_url = st.columns(2)
with col_search_kw:
    termo_busca = st.text_input("🔑 Termo / Palavra-Chave para Pesquisa:", value="Curso de Marketing Digital com Inteligência Artificial")
with col_search_url:
    url_analise = st.text_input("🌐 URL / Site para Auditoria:", value="https://www.sp.senai.br")

# Formatação segura para URLs
termo_enc = urllib.parse.quote_plus(termo_busca.strip())
url_enc = urllib.parse.quote_plus(url_analise.strip())
clean_domain = url_analise.replace("https://", "").replace("http://", "").strip().strip("/")

st.markdown("<p style='font-size: 0.9rem; font-weight: 600; color: #94a3b8; margin-top: 10px;'>⚡ Ações de 1-Clique para o Termo / Site Digitado:</p>", unsafe_allow_html=True)

btn_c1, btn_c2, btn_c3, btn_c4, btn_c5, btn_c6 = st.columns(6)

with btn_c1:
    st.link_button(
        "📈 Google Trends",
        f"https://trends.google.com.br/trends/explore?geo=BR&q={termo_enc}",
        use_container_width=True,
        help="Abre a análise de interesse e volume de busca ao longo do tempo no Google Trends Brasil"
    )
with btn_c2:
    st.link_button(
        "🔍 Google Search",
        f"https://www.google.com.br/search?q={termo_enc}",
        use_container_width=True,
        help="Verifica os resultados orgânicos e anúncios atuais no Google"
    )
with btn_c3:
    st.link_button(
        "🤖 Perplexity (GEO)",
        f"https://www.perplexity.ai/search?q={termo_enc}",
        use_container_width=True,
        help="Testa como o motor de busca com IA do Perplexity responde e cita fontes"
    )
with btn_c4:
    st.link_button(
        "⚡ PageSpeed",
        f"https://pagespeed.web.dev/analysis?url={url_enc}",
        use_container_width=True,
        help="Audita a velocidade e Core Web Vitals no Google PageSpeed Insights"
    )
with btn_c5:
    st.link_button(
        "📍 Google Maps",
        f"https://www.google.com.br/maps/search/{termo_enc}",
        use_container_width=True,
        help="Pesquisa a presença local no Google Maps para o termo informado"
    )
with btn_c6:
    st.link_button(
        "🛡️ Schema Test",
        f"https://validator.schema.org/#url={url_enc}",
        use_container_width=True,
        help="Valida a estrutura de Schema.org e Rich Results no validador oficial"
    )

st.markdown("---")

# -------------------------------------------------------------
# DIRETÓRIO CATEGORIZADO DE FERRAMENTAS E SERVIÇOS
# -------------------------------------------------------------
st.subheader("📚 Diretório Completo de Ferramentas & Serviços de Mercado")
st.caption("Selecione uma das categorias abaixo para acessar links diretos, finalidade técnica e orientações didáticas para as aulas do SENAI.")

tab_seo, tab_geo, tab_trends, tab_local, tab_ads, tab_analytics = st.tabs([
    "🔍 1. SEO & Auditoria Técnica",
    "🤖 2. GEO & AI Search Engines",
    "📈 3. Tendências & Palavras-Chave",
    "📍 4. SEO Local & Google Maps",
    "🎯 5. Mídia, Ads & Concorrência",
    "📊 6. Analytics, Tráfego & BI"
])

def render_tool_card(nome, tag, url, descricao, caso_de_uso, badge_color="#3b82f6"):
    st.markdown(f"""
    <div style='background: #1e293b; border-left: 4px solid {badge_color}; border-radius: 8px; padding: 16px; margin-bottom: 15px;'>
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
            <h4 style='margin: 0; color: #f8fafc;'>{nome}</h4>
            <span style='background: {badge_color}22; color: {badge_color}; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;'>{tag}</span>
        </div>
        <p style='color: #cbd5e1; font-size: 0.9rem; margin-bottom: 10px;'>{descricao}</p>
        <p style='color: #94a3b8; font-size: 0.85rem; margin-bottom: 12px;'><strong>💡 Aplicação na Aula:</strong> {caso_de_uso}</p>
        <a href='{url}' target='_blank' style='display: inline-block; background: #2563eb; color: #ffffff; text-decoration: none; padding: 6px 14px; border-radius: 6px; font-size: 0.85rem; font-weight: 500;'>Acessar Ferramenta ↗</a>
    </div>
    """, unsafe_allow_html=True)

# 1. SEO & Auditoria Técnica
with tab_seo:
    st.markdown("### 🔍 Ferramentas de Auditoria SEO On-Page, Off-Page & Performance")
    c1, c2 = st.columns(2)
    with c1:
        render_tool_card(
            "Google Search Console",
            "Oficial Google • Gratuito",
            "https://search.google.com/search-console/about",
            "Painel oficial do Google que mostra indexação de páginas, erros de rastreamento, cliques e impressões de palavras-chave reais.",
            "Ensinar os alunos a verificar a saúde do site, submeter Sitemaps XML e identificar termos orgânicos com alto volume de impressões."
        )
        render_tool_card(
            "Google PageSpeed Insights",
            "Oficial Google • Gratuito",
            "https://pagespeed.web.dev/",
            "Mede a pontuação dos Core Web Vitals (LCP, INP, CLS) em dispositivos móveis e computadores com recomendações técnicas.",
            "Demonstrar como a velocidade do site impacta diretamente o posicionamento orgânico e as taxas de conversão de e-commerce."
        )
        render_tool_card(
            "Schema.org & Rich Results Test",
            "Oficial Google • Gratuito",
            "https://search.google.com/test/rich-results",
            "Validador oficial de microdados e dados estruturados JSON-LD para exibição de resultados ricos (avaliações, FAQs, preços).",
            "Validar o código JSON-LD de LocalBusiness gerado no Módulo 1 do nosso laboratório."
        )
    with c2:
        render_tool_card(
            "Screaming Frog SEO Spider",
            "Crawler de Desktop • Grátis até 500 URLs",
            "https://www.screamingfrog.co.uk/seo-spider/",
            "O rastreador técnico mais famoso do mercado. Analisa links quebrados (404), títulos duplicados, meta tags e redirecionamentos.",
            "Prática de auditoria técnica profunda em laboratório de informática simulando o rastreador do Googlebot."
        )
        render_tool_card(
            "GTmetrix",
            "Performance Web • Gratuito",
            "https://gtmetrix.com/",
            "Auditoria detalhada de tempo de carregamento (Waterfall), peso das imagens e scripts JavaScript.",
            "Comparar o desempenho de sites concorrentes e diagnosticar lentidões em páginas de pouso (Landing Pages)."
        )
        render_tool_card(
            "Ahrefs Webmaster Tools (AWT)",
            "Freemium",
            "https://ahrefs.com/webmaster-tools",
            "Análise de backlinks, autoridade de domínio (DR) e verificação de links tóxicos de sites próprios.",
            "Apresentar o conceito de Link Building e autoridade de domínio (PageRank)."
        )

# 2. GEO & AI Search Engines
with tab_geo:
    st.markdown("### 🤖 Motores de Busca com Inteligência Artificial (Generative Engine Optimization - GEO)")
    st.info("💡 **O que é GEO?** É a otimização de conteúdo para que marcas e empresas sejam citadas e recomendadas por assistentes de IA (Perplexity, ChatGPT, Gemini, Copilot).")
    
    c1, c2 = st.columns(2)
    with c1:
        render_tool_card(
            "Perplexity AI",
            "Motor de Busca IA • Gratuito",
            "https://www.perplexity.ai/",
            "Motor de busca conversacional baseado em IA que cita explicitamente fontes, links e artigos acadêmicos.",
            "Testar como a IA resume o mercado e quais sites e fontes são priorizados como referência de autoridade.",
            badge_color="#10b981"
        )
        render_tool_card(
            "ChatGPT Search",
            "OpenAI • Gratuito / Plus",
            "https://chatgpt.com/",
            "Busca conectada à web da OpenAI com respostas enriquecidas com mapas, previsões e links diretos.",
            "Avaliar como o ChatGPT responde a dúvidas de compras locais ('melhores cursos em Sorocaba', 'onde comprar vestidos').",
            badge_color="#10b981"
        )
    with c2:
        render_tool_card(
            "Google Gemini com Search Grounding",
            "Google • Gratuito",
            "https://gemini.google.com/",
            "Assistente multimodal do Google conectado ao índice de pesquisa em tempo real do Google Search.",
            "Analisar a síntese de respostas geradas pelo ecossistema Gemini e AI Overviews do Google.",
            badge_color="#10b981"
        )
        render_tool_card(
            "Microsoft Copilot (Bing Search)",
            "Microsoft • Gratuito",
            "https://copilot.microsoft.com/",
            "Motor de busca com IA integrado ao Bing e ao ecossistema Microsoft Edge.",
            "Comparar as diferenças de citações entre os índices do Google e do Bing em consultas comerciais.",
            badge_color="#10b981"
        )

# 3. Tendências & Palavras-Chave
with tab_trends:
    st.markdown("### 📈 Pesquisa de Tendências, Demanda de Mercado & Intenção de Busca")
    c1, c2 = st.columns(2)
    with c1:
        render_tool_card(
            "Google Trends Brasil",
            "Oficial Google • Gratuito",
            "https://trends.google.com.br/trends/",
            "Monitoramento do interesse de busca ao longo do tempo, sazonalidade, interesse por estado/cidade e termos em ascensão.",
            "Identificar picos de interesse para planejar datas comemorativas, lançamentos de campanhas e temas para blog posts.",
            badge_color="#f59e0b"
        )
        render_tool_card(
            "Google Ads Keyword Planner",
            "Oficial Google • Gratuito",
            "https://ads.google.com/intl/pt-BR_br/home/tools/keyword-planner/",
            "Planejador oficial de palavras-chave do Google. Fornece volume mensal estimado de buscas e custo por clique (CPC).",
            "Definir orçamentos de mídia e selecionar termos de alta intenção comercial para campanhas de busca.",
            badge_color="#f59e0b"
        )
    with c2:
        render_tool_card(
            "Answer The Public",
            "Freemium",
            "https://answerthepublic.com/",
            "Mapeia todas as perguntas reais que os usuários fazem no Google (Quem, Onde, Quando, Por que, Como).",
            "Excelente para construir seções de FAQ e alimentar a base de conhecimento (RAG) dos chatbots e artigos de SEO.",
            badge_color="#f59e0b"
        )
        render_tool_card(
            "AlsoAsked",
            "Freemium",
            "https://alsoasked.com/",
            "Extrai a árvore hierárquica do bloco 'As pessoas também perguntam' (People Also Ask) do Google.",
            "Criar tópicos e subtópicos para páginas pilares e estratégias de Topic Clusters.",
            badge_color="#f59e0b"
        )

# 4. SEO Local & Google Maps
with tab_local:
    st.markdown("### 📍 Otimização para Negócios Locais, Geofencing & Google Meu Negócio")
    c1, c2 = st.columns(2)
    with c1:
        render_tool_card(
            "Perfil da Empresa no Google (Google Meu Negócio)",
            "Oficial Google • Gratuito",
            "https://www.google.com/intl/pt-BR_br/business/",
            "A ferramenta mais importante para comércios, clínicas, escolas e serviços locais. Controla aparições no Google Maps e no Local Pack.",
            "Ensinar o cadastro de NAP (Nome, Endereço, Telefone), catálogo de produtos locais, posts semanais e gestão de avaliações.",
            badge_color="#8b5cf6"
        )
    with c2:
        render_tool_card(
            "PlePer Local SEO Tools",
            "Freemium",
            "https://pleper.com/index.php?do=tools",
            "Conjunto de ferramentas para análise de categorias do Google Business Profile, pontuação de relevância local e CID finder.",
            "Auditar a escolha correta da categoria primária e secundária para ranquear no topo do Google Maps.",
            badge_color="#8b5cf6"
        )

# 5. Mídia, Ads & Concorrência
with tab_ads:
    st.markdown("### 🎯 Inteligência de Concorrência & Transparência de Anúncios")
    c1, c2 = st.columns(2)
    with c1:
        render_tool_card(
            "Google Ads Transparency Center",
            "Oficial Google • Gratuito",
            "https://adstransparency.google.com/",
            "Central pública de transparência do Google. Permite ver todos os anúncios ativos que qualquer concorrente está veiculando no Google e YouTube.",
            "Pesquisar quais criativos, títulos e ofertas os principais concorrentes do segmento estão rodando neste momento.",
            badge_color="#ef4444"
        )
    with c2:
        render_tool_card(
            "Meta Ad Library (Biblioteca de Anúncios)",
            "Oficial Meta • Gratuito",
            "https://www.facebook.com/ads/library/",
            "Repositório oficial com todos os anúncios ativos no Instagram, Facebook, Messenger e Audience Network.",
            "Análise de criativos visuais, formatos de vídeo (Reels), ganchos de copywriting e esteiras de ofertas no Meta Ads.",
            badge_color="#ef4444"
        )

# 6. Analytics & BI
with tab_analytics:
    st.markdown("### 📊 Análise de Dados, Web Analytics & Dashboards Interativos")
    c1, c2 = st.columns(2)
    with c1:
        render_tool_card(
            "Google Analytics 4 (GA4)",
            "Oficial Google • Gratuito",
            "https://analytics.google.com/",
            "A plataforma padrão de web analytics mundial, baseada em eventos, funis de conversão e inteligência preditiva do Google.",
            "Compreender a jornada do usuário, fontes de tráfego, taxas de engajamento e atribuição de conversões.",
            badge_color="#06b6d4"
        )
        render_tool_card(
            "Google Looker Studio (Data Studio)",
            "Oficial Google • Gratuito",
            "https://lookerstudio.google.com/",
            "Plataforma de criação de relatórios visuais e dashboards interativos com conexão direta ao GA4, Google Ads e planilhas.",
            "Construir painéis executivos de KPIs de Marketing para apresentação a clientes e diretoria.",
            badge_color="#06b6d4"
        )
    with c2:
        render_tool_card(
            "Google Tag Manager (GTM)",
            "Oficial Google • Gratuito",
            "https://tagmanager.google.com/",
            "Gerenciador de tags que permite instalar pixels (Meta, TikTok, Google Ads) e eventos sem mexer no código do site.",
            "Conceito de rastreamento de cliques em botões de WhatsApp, envio de formulários e compras.",
            badge_color="#06b6d4"
        )
        render_tool_card(
            "SimilarWeb",
            "Freemium",
            "https://www.similarweb.com/",
            "Estimativas de tráfego mensal, canais de aquisição e demografia de qualquer site da internet.",
            "Comparativo de Market Share e análise competitiva de tráfego de grandes portais.",
            badge_color="#06b6d4"
        )

render_sidebar_footer()
render_academic_footer()

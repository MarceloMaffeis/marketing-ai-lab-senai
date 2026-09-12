import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from bs4 import BeautifulSoup, Doctype
import pandas as pd
from urllib.parse import urljoin, urlparse
import time
import re
import requests
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
from utils.auth import check_authentication
from utils.ai_helper import render_api_key_sidebar, generate_text_ai
from utils.export_helper import generate_html_report, render_download_button
from utils.ui_components import render_sidebar_header, render_sidebar_footer, render_academic_footer

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Auditoria & Dashboard de SEO | SENAI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_sidebar_header()
check_authentication()
render_api_key_sidebar()

# --- CABEÇALHOS DE NAVEGADOR REAL ---
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1'
}

# --- BANCO DE CONHECIMENTO DE SEO (100% AUTORAL & DIDÁTICO SENAI) ---
SEO_KNOWLEDGE_BASE = {
    'Erro 4XX/5XX (Link Quebrado)': {
        'severity': 'Crítico', 'category': 'Técnico',
        'description': "Códigos de status HTTP das famílias 4xx (erro de cliente) ou 5xx (erro de servidor) indicam que o recurso solicitado não pôde ser entregue. Isso desperdiça o orçamento de rastreamento (crawl budget) dos motores de busca e resulta em abandono imediato pelo usuário.",
        'solution': "Audite as páginas de origem para corrigir links internos desatualizados. Caso a URL tenha sido removida definitivamente, configure um redirecionamento HTTP 301 permanente para o conteúdo correlato mais próximo."
    },
    'Página Bloqueada (noindex)': {
        'severity': 'Crítico', 'category': 'Indexabilidade',
        'description': "A diretiva 'noindex' (via meta tag robots ou cabeçalho HTTP X-Robots-Tag) instrui explicitamente os rastreadores a não incluírem a página no índice público da SERP, anulando qualquer oportunidade de tráfego orgânico.",
        'solution': "Se a página deve ser descoberta publicamente no Google, remova a instrução 'noindex' do código-fonte ou das configurações do seu CMS. Mantenha 'noindex' apenas em páginas administrativas, áreas de checkout ou políticas internas."
    },
    'Título Vazio': {
        'severity': 'Crítico', 'category': 'On-Page',
        'description': "O elemento <title> é o principal indicador temático utilizado pelos algoritmos de indexação e funciona como o cabeçalho clicável exibido nas páginas de resultados.",
        'solution': "Insira uma tag <title> única e descritiva para cada página, posicionando a palavra-chave de maior intenção de busca no início e o nome da organização ao final."
    },
    'Sem Tag H1': {
        'severity': 'Crítico', 'category': 'On-Page',
        'description': "A ausência de uma tag <h1> compromete a hierarquia semântica do documento HTML, dificultando a contextualização do tema principal por mecanismos de busca e tecnologias assistivas (leitores de tela).",
        'solution': "Adicione um único elemento <h1> no início do corpo da página com a proposta de valor e a palavra-chave principal do conteúdo."
    },
    'Múltiplas Tags H1': {
        'severity': 'Atenção', 'category': 'On-Page',
        'description': "A repetição de múltiplas tags <h1> em um mesmo documento fragmenta a estrutura de tópicos da página, diluindo o foco semântico do tema central.",
        'solution': "Consolide o tema principal em apenas um <h1> por documento e organize os subtópicos subsequentes utilizando <h2>, <h3> e <h4> de forma hierárquica."
    },
    'Título Muito Curto (<30c)': {
        'severity': 'Atenção', 'category': 'On-Page',
        'description': "Títulos com menos de 30 caracteres subutilizam o espaço visual disponível nos resultados de busca e fornecem contexto limitado sobre o conteúdo da página.",
        'solution': "Amplie o título inserindo qualificadores de busca, benefícios diretos do produto/serviço ou segmentação regional, buscando atingir entre 45 e 60 caracteres."
    },
    'Título Muito Longo (>65c)': {
        'severity': 'Atenção', 'category': 'On-Page',
        'description': "Títulos com mais de 65 caracteres (ou que excedam o limite visual de ~600 pixels) sofrem truncamento com reticências nos snippets do Google, ocultando termos essenciais.",
        'solution': "Edite o texto para manter as palavras-chave prioritárias nos primeiros 60 caracteres, eliminando termos redundantes."
    },
    'Meta Descrição Vazia': {
        'severity': 'Atenção', 'category': 'On-Page',
        'description': "Sem uma meta descrição configurada, o buscador exibirá trechos aleatórios capturados do corpo do texto, reduzindo a atratividade do snippet e a taxa de cliques (CTR).",
        'solution': "Escreva um resumo conciso e convidativo contendo de 120 a 155 caracteres com uma chamada para ação (CTA) persuasiva que estimule o clique do usuário."
    },
    'Meta Descrição Fora do Ideal': {
        'severity': 'Atenção', 'category': 'On-Page',
        'description': "Descrições com menos de 70 caracteres são pouco informativas, enquanto textos acima de 160 caracteres são cortados nas telas dos dispositivos móveis e desktops.",
        'solution': "Ajuste o tamanho do texto para a faixa ideal entre 120 e 155 caracteres, garantindo legibilidade completa em qualquer formato de tela."
    },
    'Conteúdo Curto (<300 palavras)': {
        'severity': 'Atenção', 'category': 'Conteúdo',
        'description': "Páginas com escassez de texto ('Thin Content') geralmente apresentam baixa densidade semântica e têm dificuldades para competir em termos concorridos nas buscas orgânicas.",
        'solution': "Enriqueça a página desenvolvendo seções detalhadas sobre benefícios, respostas para dúvidas frequentes (FAQ), dados técnicos e provas sociais."
    },
    'URL Muito Longa (>120c)': {
        'severity': 'Atenção', 'category': 'Estrutura',
        'description': "URLs excessivamente extensas ou repletas de parâmetros dinâmicos dificultam o rastreamento, o compartilhamento em redes e a legibilidade por parte do usuário.",
        'solution': "Adote URLs amigáveis e curtas (slugs limpos), estruturadas exclusivamente com palavras-chave relevantes separadas por hífens."
    },
    'Sem Certificado SSL (HTTP)': {
        'severity': 'Crítico', 'category': 'Segurança',
        'description': "Conexões em protocolo HTTP não possuem criptografia de dados, sendo sinalizadas pelos navegadores modernos como 'Não Seguras' e penalizadas nos critérios de ranqueamento.",
        'solution': "Instale um certificado SSL/TLS no servidor web e configure regras de redirecionamento automático (HTTP 301) para forçar o carregamento seguro em HTTPS."
    },
    'Sem Doctype Declarado': {
        'severity': 'Atenção', 'category': 'Técnico',
        'description': "A omissão da declaração <!DOCTYPE html> pode acionar o modo de compatibilidade retrógrada ('Quirks Mode') nos navegadores, causando inconsistências visuais e erros de renderização.",
        'solution': "Adicione a declaração <!DOCTYPE html> como a primeira linha absoluta do código-fonte antes da tag de abertura <html>."
    },
    'Imagens Sem Alt Text': {
        'severity': 'Atenção', 'category': 'Acessibilidade',
        'description': "O atributo alt fornece a descrição textual de imagens para leitores de tela de pessoas com deficiência visual e viabiliza a indexação das ilustrações no Google Imagens.",
        'solution': "Preencha o atributo alt de todas as tags <img> com descrições contextuais claras e objetivas do que a imagem representa."
    },
    'Sem Open Graph (Redes Sociais)': {
        'severity': 'Oportunidade', 'category': 'Social',
        'description': "A ausência das meta tags Open Graph (og:title, og:image, og:description) faz com que links compartilhados em aplicativos como WhatsApp e redes sociais fiquem sem imagem de prévia.",
        'solution': "Implemente as tags <meta property='og:image'> e <meta property='og:title'> no cabeçalho <head>, utilizando imagens na proporção recomendada de 1200x630 pixels."
    },
    'Sem Dados Estruturados (Schema)': {
        'severity': 'Oportunidade', 'category': 'Técnico',
        'description': "A ausência de marcação de dados estruturados em JSON-LD (Schema.org) impede os motores de busca de gerarem Rich Snippets (como estrelas de avaliação, preços e FAQs enriquecidos).",
        'solution': "Adicione esquemas em JSON-LD no cabeçalho da página compatíveis com o seu modelo de negócio (ex: Organization, LocalBusiness, Product ou Course)."
    },
    'Tag Canônica Ausente': {
        'severity': 'Atenção', 'category': 'Técnico',
        'description': "Sem a declaração da URL canônica, páginas acessíveis por múltiplas variações de links (com/sem www, parâmetros de campanha ou barras finais) podem ser tratadas como conteúdo duplicado.",
        'solution': "Insira a tag <link rel='canonical' href='URL_OFICIAL_ABSOLUTA'> no <head> de cada página para consolidar a autoridade de indexação na versão principal."
    },
    'Tempo de Resposta Lento (>1.5s)': {
        'severity': 'Atenção', 'category': 'Performance',
        'description': "Tempos elevados de resposta inicial do servidor (TTFB) e renderização aumentam a taxa de rejeição e prejudicam diretamente a pontuação nas métricas de Core Web Vitals.",
        'solution': "Comprima arquivos de mídia, utilize formatos modernos de imagem (WebP/AVIF), ative compressão Gzip/Brotli e implemente mecanismos de cache ou CDN no servidor."
    }
}

# --- FUNÇÕES DE AUDITORIA ---

def check_domain_extras(base_url, session):
    """Verifica robots.txt e sitemap.xml de forma robusta e descobre sitemaps do Yoast/WordPress/WBuy."""
    parsed = urlparse(base_url)
    root = f"{parsed.scheme}://{parsed.netloc}"
    
    results = {
        'has_robots': False,
        'robots_url': f"{root}/robots.txt",
        'has_sitemap': False,
        'sitemap_url': None
    }
    
    sitemap_from_robots = None
    
    # 1. Checagem do robots.txt
    try:
        r_robots = session.get(f"{root}/robots.txt", timeout=7, allow_redirects=True)
        if r_robots.status_code == 200 and any(k in r_robots.text.lower() for k in ['user-agent', 'disallow', 'allow', 'sitemap']):
            results['has_robots'] = True
            sm_match = re.search(r'sitemap:\s*(https?://[^\s\r\n]+)', r_robots.text, re.IGNORECASE)
            if sm_match:
                sitemap_from_robots = sm_match.group(1).strip()
    except Exception:
        pass
    
    # 2. Checagem do sitemap.xml
    candidates = []
    if sitemap_from_robots:
        candidates.append(sitemap_from_robots)
    
    candidates.extend([
        f"{root}/sitemap.xml",
        f"{root}/sitemap_index.xml",
        f"{root}/wp-sitemap.xml",
        f"{root}/sitemap/sitemap.xml"
    ])
    
    for sm_url in candidates:
        try:
            r_sitemap = session.get(sm_url, timeout=7, allow_redirects=True)
            content_lower = r_sitemap.text.lower()
            is_xml_content = '<urlset' in content_lower or '<sitemapindex' in content_lower or '<?xml' in content_lower
            if r_sitemap.status_code == 200 and is_xml_content:
                results['has_sitemap'] = True
                results['sitemap_url'] = sm_url
                break
        except Exception:
            continue
            
    return results

def crawl_website(start_url, max_pages, progress_bar, progress_text):
    """Crawler otimizado com Session e Headers persistentes."""
    if not (start_url.startswith('http://') or start_url.startswith('https://')):
        start_url = 'https://' + start_url
    
    domain = urlparse(start_url).netloc
    urls_to_visit = [start_url]
    visited_urls = set()
    pages_data = []
    
    session = requests.Session()
    session.headers.update(BROWSER_HEADERS)

    while urls_to_visit and len(visited_urls) < max_pages:
        current_url = urls_to_visit.pop(0)
        if current_url in visited_urls:
            continue
        
        visited_urls.add(current_url)
        progress_bar.progress(len(visited_urls) / max_pages)
        progress_text.text(f"Auditando ({len(visited_urls)}/{max_pages}): {current_url}")
        
        start_time = time.time()
        try:
            resp = session.get(current_url, timeout=10, allow_redirects=True)
            elapsed_time = round(time.time() - start_time, 2)
            status_code = resp.status_code
            final_url = resp.url
            html_content = resp.text
            
            if "challenge-central" in final_url or "verificando acesso" in html_content.lower():
                time.sleep(1)
                resp = session.get(current_url, timeout=10)
                html_content = resp.text
                final_url = resp.url

            soup = BeautifulSoup(html_content, 'html.parser')
            doctype_present = any(isinstance(item, Doctype) for item in soup.contents)
        except Exception:
            elapsed_time = round(time.time() - start_time, 2)
            pages_data.append({
                'URL': current_url, 'Status Code': 'Erro', 'Response Time': elapsed_time,
                'Title': '', 'Meta Description': '', 'Word Count': 0, 'H1 Count': 0,
                'H1 Text': '', 'Has Doctype': False, 'Is Noindex': False, 'Imagens_Sem_Alt': 0,
                'Total_Imagens': 0, 'Links_Internos': 0, 'Links_Externos': 0, 'Possui_Schema': False,
                'Possui_OG': False, 'Canonical_URL': None
            })
            continue

        if soup:
            title_tag = soup.find('title')
            title = title_tag.text.strip() if title_tag else ""
            
            meta_desc_tag = soup.find('meta', attrs={'name': lambda x: x and x.lower() == 'description'})
            meta_desc = meta_desc_tag['content'].strip() if (meta_desc_tag and meta_desc_tag.get('content')) else ""
            
            body_text = soup.body.get_text(separator=' ', strip=True) if soup.body else ""
            clean_text = re.sub(r'\s+', ' ', body_text)
            word_count = len(clean_text.split()) if clean_text else 0
            
            h1_tags = [h.get_text(strip=True) for h in soup.find_all('h1')]
            
            meta_robots = soup.find('meta', attrs={'name': lambda x: x and x.lower() == 'robots'})
            is_noindex = bool(meta_robots and 'noindex' in str(meta_robots.get('content', '')).lower())
            
            images = soup.find_all('img')
            missing_alt = sum(1 for img in images if not img.get('alt', '').strip())
            
            int_links, ext_links = 0, 0
            for a in soup.find_all('a', href=True):
                href = a['href']
                abs_url = urljoin(final_url, href).split('#')[0]
                parsed_link = urlparse(abs_url)
                
                base_clean = domain.replace('www.', '')
                link_clean = parsed_link.netloc.replace('www.', '')
                
                if link_clean == base_clean:
                    int_links += 1
                    if abs_url not in visited_urls and abs_url not in urls_to_visit and abs_url.startswith('http'):
                        urls_to_visit.append(abs_url)
                elif parsed_link.scheme in ['http', 'https']:
                    ext_links += 1
            
            has_schema = bool(soup.find('script', type='application/ld+json'))
            has_og = bool(soup.find('meta', property=re.compile(r'^og:')))
            
            canonical_tag = soup.find('link', rel='canonical')
            canonical_url = canonical_tag['href'] if (canonical_tag and canonical_tag.get('href')) else None

            pages_data.append({
                'URL': final_url, 'Status Code': status_code, 'Response Time': elapsed_time,
                'Title': title, 'Meta Description': meta_desc, 'Word Count': word_count,
                'H1 Count': len(h1_tags), 'H1 Text': " | ".join(h1_tags), 'Has Doctype': doctype_present,
                'Is Noindex': is_noindex, 'Imagens_Sem_Alt': missing_alt, 'Total_Imagens': len(images),
                'Links_Internos': int_links, 'Links_Externos': ext_links, 'Possui_Schema': has_schema,
                'Possui_OG': has_og, 'Canonical_URL': canonical_url
            })
            
    progress_bar.empty()
    progress_text.empty()
    return pd.DataFrame(pages_data), session

def evaluate_page_issues(row):
    """Verifica regras de SEO por página."""
    issues = []
    
    if isinstance(row['Status Code'], int) and row['Status Code'] >= 400:
        issues.append('Erro 4XX/5XX (Link Quebrado)')
    
    if not row['Title']:
        issues.append('Título Vazio')
    elif len(row['Title']) < 30:
        issues.append('Título Muito Curto (<30c)')
    elif len(row['Title']) > 65:
        issues.append('Título Muito Longo (>65c)')
        
    if not row['Meta Description']:
        issues.append('Meta Descrição Vazia')
    elif len(row['Meta Description']) < 70 or len(row['Meta Description']) > 160:
        issues.append('Meta Descrição Fora do Ideal')
        
    if row['H1 Count'] == 0:
        issues.append('Sem Tag H1')
    elif row['H1 Count'] > 1:
        issues.append('Múltiplas Tags H1')
        
    if row['Word Count'] < 300:
        issues.append('Conteúdo Curto (<300 palavras)')
        
    if row['Is Noindex']:
        issues.append('Página Bloqueada (noindex)')
    if not urlparse(row['URL']).scheme == 'https':
        issues.append('Sem Certificado SSL (HTTP)')
    if not row['Has Doctype']:
        issues.append('Sem Doctype Declarado')
    if len(row['URL']) > 120:
        issues.append('URL Muito Longa (>120c)')
    if row['Imagens_Sem_Alt'] > 0:
        issues.append('Imagens Sem Alt Text')
    if not row['Possui_Schema']:
        issues.append('Sem Dados Estruturados (Schema)')
    if not row['Possui_OG']:
        issues.append('Sem Open Graph (Redes Sociais)')
    if not row['Canonical_URL']:
        issues.append('Tag Canônica Ausente')
    if isinstance(row['Response Time'], (int, float)) and row['Response Time'] > 1.5:
        issues.append('Tempo de Resposta Lento (>1.5s)')

    return issues

def calculate_seo_health_score(df, domain_extras):
    """Calcula Score de 0 a 100 de forma balanceada."""
    if df.empty: return 0
    total_pages = len(df)
    total_deductions = 0
    
    penalties = {'Crítico': 12, 'Atenção': 4, 'Oportunidade': 2}
    
    for issues in df['Issues_List']:
        for issue in issues:
            sev = SEO_KNOWLEDGE_BASE.get(issue, {}).get('severity', 'Atenção')
            total_deductions += penalties.get(sev, 4)
            
    if not domain_extras.get('has_robots'): total_deductions += 8
    if not domain_extras.get('has_sitemap'): total_deductions += 8
    
    max_penalty = total_pages * 25 + 16
    score = max(10, int(100 - (total_deductions / max_penalty * 100)))
    return min(100, score)

# --- COMPONENTES VISUAIS ---

def render_gauge_score(score):
    color = "#2ecc71" if score >= 80 else "#f39c12" if score >= 50 else "#e74c3c"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "SEO Health Score", 'font': {'size': 20, 'color': '#cbd5e1'}},
        number={'suffix': "/100", 'font': {'size': 30, 'color': color}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': "#1e293b",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 49], 'color': 'rgba(231, 76, 60, 0.2)'},
                {'range': [50, 79], 'color': 'rgba(243, 156, 18, 0.2)'},
                {'range': [80, 100], 'color': 'rgba(46, 204, 113, 0.2)'}
            ]
        }
    ))
    fig.update_layout(height=240, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

def render_serp_preview(title, url, description):
    clean_title = title if title else "Título da Página Não Encontrado"
    clean_desc = description if description else "Nenhuma meta descrição informada. O Google criará um resumo automático baseado no conteúdo."
    display_url = url if len(url) < 65 else url[:62] + "..."
    
    st.markdown(f"""
    <div style="background-color: #ffffff; padding: 16px; border-radius: 8px; border: 1px solid #dfe1e5; max-width: 650px; font-family: Roboto, Arial, sans-serif; box-shadow: 0 1px 4px rgba(32,33,36,.12); color: #202124;">
        <div style="font-size: 12px; color: #202124; margin-bottom: 2px;">{display_url}</div>
        <div style="font-size: 18px; color: #1a0dab; text-decoration: none; font-weight: 400; margin-bottom: 3px; line-height: 1.3;">
            {clean_title}
        </div>
        <div style="font-size: 13px; color: #4d5156; line-height: 1.4;">
            {clean_desc}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- INTERFACE PRINCIPAL ---

st.title("🔍 Auditoria de SEO & Otimização Web")
st.caption("Alinhado aos **Módulos 1 e 5 da Ementa SENAI**: Reconhecimento dos pilares do marketing digital, tráfego orgânico, SEO On-Page, análise técnica e experiência do usuário.")

st.markdown("---")

with st.sidebar:
    st.header("⚙️ Configurações da Auditoria")
    target_url = st.text_input("🌐 Domínio / URL Principal", value="https://www.reed7.com.br/")
    max_pages = st.slider("📄 Limite de Páginas para Varrer", min_value=5, max_value=50, value=15, step=5)
    
    st.markdown("---")
    st.subheader("👥 Benchmarking Competitivo")
    comp_url_1 = st.text_input("Concorrente 1 (Opcional)", value="https://www.estampariavasconcelos.com.br/")
    comp_url_2 = st.text_input("Concorrente 2 (Opcional)", value="https://oreidoabada.com/")
    
    run_audit = st.button("🚀 Iniciar Auditoria Completa", type="primary", use_container_width=True)

if run_audit:
    if not target_url:
        st.warning("⚠️ Por favor, insira a URL principal para iniciar.")
    else:
        urls_to_scan = [target_url]
        if comp_url_1 and comp_url_1.strip(): urls_to_scan.append(comp_url_1.strip())
        if comp_url_2 and comp_url_2.strip(): urls_to_scan.append(comp_url_2.strip())
        
        all_results = []
        domain_extras_map = {}
        
        progress_box = st.container()
        progress_bar = progress_box.progress(0)
        progress_text = progress_box.empty()
        
        for u in urls_to_scan:
            domain_name = urlparse('https://' + re.sub(r'^(https?://)', '', u)).netloc
            st.info(f"🔎 Analisando domínio: **{domain_name}**...")
            
            df_crawled, active_session = crawl_website(u, max_pages, progress_bar, progress_text)
            domain_extras_map[domain_name] = check_domain_extras(u, active_session)
            
            if not df_crawled.empty:
                df_crawled['Domínio'] = domain_name
                df_crawled['Issues_List'] = df_crawled.apply(evaluate_page_issues, axis=1)
                df_crawled['Problemas_Str'] = df_crawled['Issues_List'].apply(lambda x: ', '.join(x) if x else 'OK')
                all_results.append(df_crawled)
                
        if not all_results:
            st.error("❌ Não foi possível extrair dados dos sites informados. Verifique a URL digitada.")
        else:
            full_df = pd.concat(all_results, ignore_index=True)
            main_domain = urlparse('https://' + re.sub(r'^(https?://)', '', target_url)).netloc
            main_df = full_df[full_df['Domínio'] == main_domain].copy()
            main_extras = domain_extras_map.get(main_domain, {'has_robots': False, 'has_sitemap': False, 'sitemap_url': None})
            
            health_score = calculate_seo_health_score(main_df, main_extras)
            
            st.success("✅ Auditoria finalizada com sucesso!")
            
            tab_client, tab_actions, tab_ai, tab_tech, tab_comp = st.tabs([
                "📊 Visão Executiva (Dashboard)",
                "🎯 Plano de Ação Priorizado",
                "🤖 Diagnóstico com IA",
                "🛠️ Auditoria Técnica Detalhada",
                "🏆 Benchmarking Competitivo"
            ])
            
            # --- ABA 1: DASHBOARD EXECUTIVO ---
            with tab_client:
                st.subheader(f"Resumo Geral de Desempenho: **{main_domain}**")
                
                c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1.2])
                with c1:
                    st.plotly_chart(render_gauge_score(health_score), use_container_width=True)
                with c2:
                    st.metric("Páginas Auditadas", len(main_df))
                    pages_with_issues = len(main_df[main_df['Problemas_Str'] != 'OK'])
                    st.metric("Páginas com Oportunidades", pages_with_issues)
                with c3:
                    avg_words = int(main_df['Word Count'].mean()) if not main_df.empty else 0
                    st.metric("Média de Palavras / Página", f"{avg_words} palavras")
                    avg_time = round(main_df['Response Time'].mean(), 2) if not main_df.empty else 0
                    st.metric("Tempo Médio de Resposta", f"{avg_time}s")
                with c4:
                    st.markdown("**Status de Indexabilidade Global:**")
                    st.write(f"• **robots.txt**: {'✅ Presente' if main_extras['has_robots'] else '❌ Ausente'}")
                    if main_extras['has_sitemap']:
                        s_name = main_extras['sitemap_url'].split('/')[-1] if main_extras.get('sitemap_url') else 'sitemap.xml'
                        st.write(f"• **sitemap.xml**: ✅ Presente (`{s_name}`)")
                    else:
                        st.write(f"• **sitemap.xml**: ❌ Ausente")
                    ssl_active = all(main_df['URL'].str.startswith('https'))
                    st.write(f"• **Certificado SSL**: {'✅ 100% HTTPS' if ssl_active else '⚠️ Contém HTTP'}")

                st.markdown("---")
                
                col_g1, col_g2 = st.columns(2)
                all_issues = [issue for sublist in main_df['Issues_List'] for issue in sublist]
                issue_counter = Counter(all_issues)
                
                with col_g1:
                    st.subheader("Distribuição por Severidade")
                    if issue_counter:
                        sev_data = []
                        for issue, count in issue_counter.items():
                            sev = SEO_KNOWLEDGE_BASE.get(issue, {}).get('severity', 'Atenção')
                            sev_data.append({'Severidade': sev, 'Ocorrências': count})
                        sev_df = pd.DataFrame(sev_data).groupby('Severidade').sum().reset_index()
                        fig_sev = px.pie(
                            sev_df, names='Severidade', values='Ocorrências',
                            color='Severidade',
                            color_discrete_map={'Crítico': '#e74c3c', 'Atenção': '#f39c12', 'Oportunidade': '#3498db'},
                            hole=0.45
                        )
                        fig_sev.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                        st.plotly_chart(fig_sev, use_container_width=True)
                    else:
                        st.success("Nenhum problema encontrado!")

                with col_g2:
                    st.subheader("Top Oportunidades de Otimização")
                    if issue_counter:
                        top_issues_df = pd.DataFrame(issue_counter.most_common(6), columns=['Item', 'Páginas Afetadas'])
                        fig_bar = px.bar(
                            top_issues_df, x='Páginas Afetadas', y='Item', orientation='h',
                            color='Páginas Afetadas', color_continuous_scale='Reds'
                        )
                        fig_bar.update_layout(yaxis={'autorange': 'reversed'}, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                        st.plotly_chart(fig_bar, use_container_width=True)
                    else:
                        st.info("Tudo otimizado!")

                st.markdown("---")
                st.subheader("👀 Prévia da Home no Google (SERP Preview)")
                home_row = main_df.iloc[0]
                render_serp_preview(home_row['Title'], home_row['URL'], home_row['Meta Description'])

            # --- ABA 2: PLANO DE AÇÃO ---
            with tab_actions:
                st.subheader("📋 Plano de Ação Recomendado (Priorizado)")
                st.caption("Abaixo estão listados os problemas encontrados no seu site com explicações e orientações práticas de correção:")
                
                if not issue_counter:
                    st.success("🎉 Parabéns! Não foram encontrados problemas graves.")
                else:
                    sorted_unique_issues = sorted(
                        issue_counter.keys(),
                        key=lambda x: (0 if SEO_KNOWLEDGE_BASE.get(x, {}).get('severity') == 'Crítico' else 1 if SEO_KNOWLEDGE_BASE.get(x, {}).get('severity') == 'Atenção' else 2)
                    )
                    
                    for issue in sorted_unique_issues:
                        info = SEO_KNOWLEDGE_BASE.get(issue, {'severity': 'Atenção', 'description': '', 'solution': ''})
                        badge_color = "🔴" if info['severity'] == 'Crítico' else "🟡" if info['severity'] == 'Atenção' else "🔵"
                        
                        affected_df = main_df[main_df['Issues_List'].apply(lambda l: issue in l)][['URL', 'Title']]
                        
                        with st.expander(f"{badge_color} **{issue}** — {len(affected_df)} página(s) afetada(s) [{info['severity']}]"):
                            st.markdown("**📖 O que é isso?**")
                            st.write(info['description'])
                            st.markdown("**🛠️ Como solucionar?**")
                            st.info(info['solution'])
                            st.markdown("**URLs Afetadas:**")
                            st.dataframe(affected_df, use_container_width=True)

            # --- ABA 3: DIAGNÓSTICO COM IA ---
            with tab_ai:
                st.subheader("🤖 Consultor de SEO & Estratégia de Tráfego com IA")
                st.write("A Inteligência Artificial analisa o Health Score e os problemas técnicos para gerar uma recomendação estratégica:")
                
                top_3_issues = [f"{item[0]} ({item[1]} páginas)" for item in issue_counter.most_common(3)]
                issues_summary_str = ", ".join(top_3_issues) if top_3_issues else "Nenhum problema grave."
                
                prompt_ai = f"""
                Você é um especialista em SEO técnico, marketing de conteúdo e otimização de conversão.
                Analise os seguintes dados da auditoria do site {main_domain}:
                - Health Score: {health_score}/100
                - Total de páginas auditadas: {len(main_df)}
                - Principais problemas encontrados: {issues_summary_str}
                - robots.txt: {'Presente' if main_extras['has_robots'] else 'Ausente'}
                - sitemap.xml: {'Presente' if main_extras['has_sitemap'] else 'Ausente'}
                - Média de palavras por página: {avg_words}
                - Tempo médio de resposta: {avg_time}s
                
                Gere um parecer executivo contendo:
                1. Diagnóstico Geral do Site (em 2 parágrafos objetivos).
                2. 3 Ações Imediatas de Alto Impacto para ranquear no Google.
                3. Sugestão de Pauta / Palavras-chave estratégicas para aumentar o tráfego orgânico.
                Formate em Markdown limpo com tópicos.
                """
                
                with st.spinner("Gerando diagnóstico estratégico com IA..."):
                    diagnostico_ia = generate_text_ai(prompt_ai, "Você é um consultor sênior de SEO do SENAI.")
                    
                    if not diagnostico_ia:
                        diagnostico_ia = f"""### 📊 Parecer Executivo de SEO • {main_domain}

**1. Diagnóstico Geral:**
O domínio **{main_domain}** obteve um **SEO Health Score de {health_score}/100**. {'O site apresenta boa base técnica, necessitando apenas de ajustes finos em tags e densidade de conteúdo.' if health_score >= 70 else 'Foram identificados gargalos importantes que estão limitando o potencial de indexação e autoridade no Google.'}

**2. Ações Prioritárias Recomendadas:**
- **Correção dos Principais Erros:** Focar na resolução imediata de *{issues_summary_str}*.
- **Enriquecimento de Conteúdo:** Elevar a média de palavras ({avg_words} palavras atuais) para no mínimo 600 palavras nas páginas centrais de produtos/serviços.
- **Estrutura Técnica:** {'Garantir submissão do sitemap.xml no Google Search Console.' if not main_extras['has_sitemap'] else 'Manter sitemap.xml e robots.txt sempre sincronizados.'}

**3. Oportunidades de Tráfego Orgânico:**
- Criar páginas de destino (Landing Pages) focadas em palavras-chave de cauda longa (*long-tail keywords*) com intenção comercial clara.
- Otimizar títulos e meta descrições para aumentar o CTR na página de resultados do Google (SERP).
"""
                st.markdown(diagnostico_ia)

            # --- ABA 4: AUDITORIA TÉCNICA DETALHADA ---
            with tab_tech:
                st.subheader("📄 Tabela Completa de URLs Auditadas")
                st.dataframe(
                    main_df[['URL', 'Status Code', 'Response Time', 'Title', 'Word Count', 'H1 Count', 'Imagens_Sem_Alt', 'Possui_Schema', 'Possui_OG', 'Problemas_Str']],
                    use_container_width=True,
                    height=450
                )
                
                csv_data = main_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "⬇️ Baixar Tabela em CSV",
                    data=csv_data,
                    file_name=f"auditoria_seo_{main_domain}.csv",
                    mime="text/csv"
                )

            # --- ABA 5: BENCHMARKING COMPETITIVO ---
            with tab_comp:
                st.subheader("🏆 Comparativo com Concorrentes")
                if len(full_df['Domínio'].unique()) < 2:
                    st.info("💡 Para visualizar o comparativo, insira a URL de ao menos um concorrente na barra lateral.")
                else:
                    comp_summary = full_df.groupby('Domínio').agg(
                        Páginas_Auditadas=('URL', 'count'),
                        Média_Palavras=('Word Count', 'mean'),
                        Média_Links_Internos=('Links_Internos', 'mean'),
                        Tempo_Medio_Resposta=('Response Time', 'mean')
                    ).reset_index()
                    
                    st.dataframe(comp_summary.style.format({
                        'Média_Palavras': '{:.0f}',
                        'Média_Links_Internos': '{:.1f}',
                        'Tempo_Medio_Resposta': '{:.2f}s'
                    }), use_container_width=True)
                    
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        fig_words = px.bar(comp_summary, x='Domínio', y='Média_Palavras', title="Profundidade Média de Conteúdo (Palavras)", color='Domínio')
                        fig_words.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                        st.plotly_chart(fig_words, use_container_width=True)
                    with col_b2:
                        fig_speed = px.bar(comp_summary, x='Domínio', y='Tempo_Medio_Resposta', title="Tempo de Resposta (Segundos - Menor é melhor)", color='Domínio')
                        fig_speed.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                        st.plotly_chart(fig_speed, use_container_width=True)

            # --- EXPORTAR RELATÓRIO COMPLETO EM HTML ---
            st.markdown("---")
            st.subheader("📥 Leve seu Relatório de SEO para Casa")
            
            top_issues_html = "<ul>" + "".join([f"<li><strong>{item[0]}:</strong> {item[1]} página(s) afetada(s)</li>" for item in issue_counter.most_common(5)]) + "</ul>" if issue_counter else "<p>Nenhum problema grave encontrado.</p>"
            
            secoes_seo = [
                ("1. Sumário Executivo do Site", f"<p><strong>Domínio Auditado:</strong> {main_domain}<br><strong>SEO Health Score:</strong> {health_score}/100<br><strong>Total de Páginas Varridas:</strong> {len(main_df)}<br><strong>robots.txt:</strong> {'Presente' if main_extras['has_robots'] else 'Ausente'}<br><strong>sitemap.xml:</strong> {'Presente' if main_extras['has_sitemap'] else 'Ausente'}</p>"),
                ("2. Principais Oportunidades Identificadas", top_issues_html),
                ("3. Diagnóstico e Parecer Estratégico com IA", f"<pre>{diagnostico_ia}</pre>")
            ]
            
            html_seo = generate_html_report(
                title=f"Relatório de Auditoria SEO: {main_domain}",
                subtitle="Diagnóstico de Indexabilidade, Conteúdo & Otimização Técnica — SENAI",
                sections=secoes_seo
            )
            
            render_download_button(
                label="📥 Baixar Relatório Completo de Auditoria SEO em HTML",
                data=html_seo,
                file_name=f"auditoria_seo_{main_domain}.html",
                mime="text/html"
            )

else:
    st.info("👈 Insira a URL do site na barra lateral esquerda e clique em **Iniciar Auditoria Completa** para varrer o site e gerar os diagnósticos.")

render_sidebar_footer()
render_academic_footer()

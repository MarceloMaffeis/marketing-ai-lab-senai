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
import math
import json
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
    page_title="Auditoria SEO, GEO & Geomarketing | SENAI",
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

# --- CRAWLERS DE INTELIGÊNCIA ARTIFICIAL (GEO) ---
AI_BOTS_DIRECTORY = {
    'GPTBot': {'empresa': 'OpenAI', 'funcao': 'Indexação para ChatGPT Search e treinamento'},
    'ChatGPT-User': {'empresa': 'OpenAI', 'funcao': 'Navegação em tempo real sob demanda do usuário'},
    'Google-Extended': {'empresa': 'Google', 'funcao': 'Alimentação do Gemini e Vertex AI'},
    'PerplexityBot': {'empresa': 'Perplexity AI', 'funcao': 'Busca conversacional e citações de fontes'},
    'ClaudeBot': {'empresa': 'Anthropic', 'funcao': 'Busca na web e citações pelo Claude'},
    'Bytespider': {'empresa': 'ByteDance', 'funcao': 'Indexação para buscas no TikTok e IA'},
    'CCBot': {'empresa': 'Common Crawl', 'funcao': 'Dataset aberto de treinamento de LLMs'}
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
        'description': "A ausência de marcação de dados estruturados em JSON-LD (Schema.org) impede os motores de busca de gerarem Rich Snippets (como estrelas de avaliação, preços e FAQs enriquecidos) e prejudica a extração por IAs generativas.",
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

# --- FUNÇÕES DE AUDITORIA & PARSING ---

def parse_ai_bots_in_robots(robots_text):
    """Analisa permissões para crawlers de IA Generativa dentro do robots.txt."""
    if not robots_text:
        return {bot: {'status': 'Neutro (Sem robots.txt)', 'badge': '⚪', 'allowed': True, 'details': AI_BOTS_DIRECTORY[bot]} for bot in AI_BOTS_DIRECTORY}
    
    rules = {}
    current_agents = []
    
    for raw_line in robots_text.splitlines():
        line = raw_line.split('#')[0].strip()
        if not line or ':' not in line:
            continue
        key, val = line.split(':', 1)
        key = key.strip().lower()
        val = val.strip()
        
        if key == 'user-agent':
            current_agents.append(val.lower())
        elif key in ['disallow', 'allow']:
            for agent in current_agents:
                if agent not in rules:
                    rules[agent] = []
                rules[agent].append((key, val))
        else:
            current_agents = []
            
    bot_results = {}
    for bot_name, meta in AI_BOTS_DIRECTORY.items():
        bot_lower = bot_name.lower()
        status = "Permitido (Sem restrições)"
        badge = "🟢"
        allowed = True
        
        if bot_lower in rules:
            disallows = [p for r_type, p in rules[bot_lower] if r_type == 'disallow']
            allows = [p for r_type, p in rules[bot_lower] if r_type == 'allow']
            if '/' in disallows and not allows:
                status = "Bloqueado Totalmente (Disallow: /)"
                badge = "🔴"
                allowed = False
            elif disallows:
                status = f"Bloqueio Parcial ({len(disallows)} rotas)"
                badge = "🟡"
                allowed = True
            else:
                status = "Explicitamente Permitido"
                badge = "🟢"
                allowed = True
        elif '*' in rules:
            star_disallows = [p for r_type, p in rules['*'] if r_type == 'disallow']
            if '/' in star_disallows:
                status = "Bloqueado por Regra Geral (*)"
                badge = "🔴"
                allowed = False
            elif star_disallows:
                status = f"Restrições Gerais (*)"
                badge = "🟡"
                allowed = True
            else:
                status = "Permitido (Regra Geral)"
                badge = "🟢"
                allowed = True
                
        bot_results[bot_name] = {
            'status': status,
            'badge': badge,
            'allowed': allowed,
            'details': meta
        }
        
    return bot_results

def check_domain_extras(base_url, session):
    """Verifica robots.txt, crawlers de IA e sitemap.xml."""
    parsed = urlparse(base_url)
    root = f"{parsed.scheme}://{parsed.netloc}"
    
    results = {
        'has_robots': False,
        'robots_url': f"{root}/robots.txt",
        'robots_text': "",
        'ai_bots': {},
        'has_sitemap': False,
        'sitemap_url': None
    }
    
    sitemap_from_robots = None
    
    try:
        r_robots = session.get(f"{root}/robots.txt", timeout=7, allow_redirects=True)
        if r_robots.status_code == 200 and any(k in r_robots.text.lower() for k in ['user-agent', 'disallow', 'allow', 'sitemap']):
            results['has_robots'] = True
            results['robots_text'] = r_robots.text
            sm_match = re.search(r'sitemap:\s*(https?://[^\s]+)', r_robots.text, re.IGNORECASE)
            if sm_match:
                sitemap_from_robots = sm_match.group(1).strip()
    except Exception:
        pass
    
    results['ai_bots'] = parse_ai_bots_in_robots(results['robots_text'])
    
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
    """Crawler com extração de tags on-page e semântica para SEO e GEO."""
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
                'H1 Text': '', 'H2 Count': 0, 'Has Doctype': False, 'Is Noindex': False, 'Imagens_Sem_Alt': 0,
                'Total_Imagens': 0, 'Links_Internos': 0, 'Links_Externos': 0, 'Possui_Schema': False,
                'Possui_OG': False, 'Canonical_URL': None, 'Lists_Count': 0, 'Snippet_Text': ''
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
            h2_tags = [h.get_text(strip=True) for h in soup.find_all('h2')]
            lists_count = len(soup.find_all(['ul', 'ol', 'dl']))
            
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

            # Amostra de texto para visualização e IA
            first_p = soup.find('p')
            sample_snippet = first_p.get_text(strip=True) if first_p else (clean_text[:200] if clean_text else "")

            pages_data.append({
                'URL': final_url, 'Status Code': status_code, 'Response Time': elapsed_time,
                'Title': title, 'Meta Description': meta_desc, 'Word Count': word_count,
                'H1 Count': len(h1_tags), 'H1 Text': " | ".join(h1_tags),
                'H2 Count': len(h2_tags), 'Has Doctype': doctype_present,
                'Is Noindex': is_noindex, 'Imagens_Sem_Alt': missing_alt, 'Total_Imagens': len(images),
                'Links_Internos': int_links, 'Links_Externos': ext_links, 'Possui_Schema': has_schema,
                'Possui_OG': has_og, 'Canonical_URL': canonical_url,
                'Lists_Count': lists_count, 'Snippet_Text': sample_snippet[:250]
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
    """Calcula SEO Health Score de 0 a 100."""
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

def calculate_geo_readiness_score(df, domain_extras):
    """Calcula pontuação de prontidão para motores de IA (GEO Readiness Score: 0 a 100)."""
    if df.empty: return 0
    score = 0
    
    # 1. Permissões de Bots de IA no robots.txt (até 25 pts)
    ai_bots = domain_extras.get('ai_bots', {})
    allowed_bots = sum(1 for b in ai_bots.values() if b.get('allowed', True))
    total_bots = len(ai_bots) if ai_bots else 1
    score += int((allowed_bots / total_bots) * 25)
    
    # 2. Dados Estruturados Schema.org (até 25 pts)
    schema_ratio = df['Possui_Schema'].mean() if 'Possui_Schema' in df else 0
    score += int(schema_ratio * 25)
    
    # 3. Profundidade e Densidade Semântica (até 25 pts)
    avg_words = df['Word Count'].mean() if 'Word Count' in df else 0
    if avg_words >= 600: score += 25
    elif avg_words >= 350: score += 18
    elif avg_words >= 200: score += 10
    else: score += 5
    
    # 4. Estrutura de Extração Direta - H2s e Listas (até 25 pts)
    has_h2 = (df['H2 Count'] > 0).mean() if 'H2 Count' in df else 0
    has_lists = (df['Lists_Count'] > 0).mean() if 'Lists_Count' in df else 0
    score += int((has_h2 * 0.5 + has_lists * 0.5) * 25)
    
    return min(100, max(15, score))

# --- COMPONENTES VISUAIS ---

def render_gauge_score(score, title="SEO Health Score"):
    color = "#2ecc71" if score >= 80 else "#f39c12" if score >= 50 else "#e74c3c"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 18, 'color': '#cbd5e1'}},
        number={'suffix': "/100", 'font': {'size': 28, 'color': color}},
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
    fig.update_layout(height=230, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
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

# --- CABEÇALHO DA PÁGINA ---
st.title("🔍 Auditoria de SEO, GEO & Geomarketing")
st.caption("Alinhado ao **Módulo 1 da Ementa SENAI**: Fundamentos do Marketing Digital, Tráfego Orgânico, SEO On-Page, **GEO** (*Generative Engine Optimization* para ChatGPT/Perplexity), **Geomarketing & SEO Local** e **Pesquisa de Palavras-Chave & Cauda Longa**.")

st.markdown("---")

# --- PAINEL DE CONFIGURAÇÃO DA AUDITORIA (NO CORPO DA PÁGINA) ---
st.markdown("### ⚙️ Painel de Configuração da Auditoria")
with st.container():
    col_cfg1, col_cfg2 = st.columns([2.3, 1.2])
    with col_cfg1:
        target_url = st.text_input(
            "🌐 Domínio ou URL Principal para Auditar:",
            value="https://www.sp.senai.br/unidade/sorocaba/",
            help="Insira o link completo (com https://) do portal do SENAI SP, da sua empresa ou projeto integrador."
        )
    with col_cfg2:
        max_pages = st.slider(
            "📄 Limite de Páginas para Varrer:",
            min_value=1,
            max_value=50,
            value=1,
            step=1,
            help="Defina 1 para auditar apenas a página inicial (Home/URL informada) ou aumente para varrer páginas internas do domínio."
        )

    with st.expander("👥 Benchmarking Competitivo — Adicionar Concorrentes (Opcional)", expanded=False):
        col_comp1, col_comp2 = st.columns(2)
        with col_comp1:
            comp_url_1 = st.text_input("Concorrente 1 (URL Completa):", value="", placeholder="Ex: https://www.fatecsp.br/")
        with col_comp2:
            comp_url_2 = st.text_input("Concorrente 2 (URL Completa):", value="", placeholder="Ex: https://www.etec.sp.gov.br/")

    run_audit = st.button("🚀 Iniciar Auditoria Completa de SEO, GEO & Local", type="primary", use_container_width=True)

st.markdown("---")

# Armazenamento em Session State para persistência entre cliques
if run_audit or "last_audit_data" in st.session_state:
    if run_audit:
        if not target_url:
            st.warning("⚠️ Por favor, insira a URL principal para iniciar.")
            st.stop()
            
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
            st.stop()
            
        full_df = pd.concat(all_results, ignore_index=True)
        main_domain = urlparse('https://' + re.sub(r'^(https?://)', '', target_url)).netloc
        main_df = full_df[full_df['Domínio'] == main_domain].copy()
        main_extras = domain_extras_map.get(main_domain, {'has_robots': False, 'has_sitemap': False, 'sitemap_url': None, 'ai_bots': {}})
        
        health_score = calculate_seo_health_score(main_df, main_extras)
        geo_score = calculate_geo_readiness_score(main_df, main_extras)
        
        st.session_state["last_audit_data"] = {
            "full_df": full_df,
            "main_df": main_df,
            "main_domain": main_domain,
            "main_extras": main_extras,
            "health_score": health_score,
            "geo_score": geo_score
        }
    else:
        cached = st.session_state["last_audit_data"]
        full_df = cached["full_df"]
        main_df = cached["main_df"]
        main_domain = cached["main_domain"]
        main_extras = cached["main_extras"]
        health_score = cached["health_score"]
        geo_score = cached["geo_score"]

    st.success(f"✅ Auditoria ativa para **{main_domain}** ({len(main_df)} páginas analisadas)!")

    # --- NAVEGAÇÃO POR ABAS EXPANDIDA COM OS 2 PILARES DE GEO ---
    tab_client, tab_actions, tab_ai, tab_geo_ai, tab_geomarketing, tab_keywords, tab_tech, tab_comp = st.tabs([
        "📊 Visão Executiva (Dashboard)",
        "🎯 Plano de Ação Priorizado",
        "🤖 Diagnóstico com IA",
        "⚡ GEO: Otimização para IA Search",
        "📍 GEO: Geomarketing & SEO Local",
        "🔑 Palavras-Chave & Cauda Longa",
        "🛠️ Auditoria Técnica Detalhada",
        "🏆 Benchmarking Competitivo"
    ])

    all_issues = [issue for sublist in main_df['Issues_List'] for issue in sublist]
    issue_counter = Counter(all_issues)
    avg_words = int(main_df['Word Count'].mean()) if not main_df.empty else 0
    avg_time = round(main_df['Response Time'].mean(), 2) if not main_df.empty else 0

    # ==========================================
    # --- ABA 1: DASHBOARD EXECUTIVO ---
    # ==========================================
    with tab_client:
        st.subheader(f"Resumo Geral de Desempenho: **{main_domain}**")
        
        c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1.2])
        with c1:
            st.plotly_chart(render_gauge_score(health_score, "SEO Health Score"), use_container_width=True)
        with c2:
            st.metric("Páginas Auditadas", len(main_df))
            pages_with_issues = len(main_df[main_df['Problemas_Str'] != 'OK'])
            st.metric("Páginas com Oportunidades", pages_with_issues)
        with c3:
            st.metric("Média de Palavras / Página", f"{avg_words} palavras")
            st.metric("Tempo Médio de Resposta", f"{avg_time}s")
        with c4:
            st.markdown("**Status de Indexabilidade Global:**")
            st.write(f"• **robots.txt**: {'✅ Presente' if main_extras.get('has_robots') else '❌ Ausente'}")
            if main_extras.get('has_sitemap'):
                s_name = main_extras['sitemap_url'].split('/')[-1] if main_extras.get('sitemap_url') else 'sitemap.xml'
                st.write(f"• **sitemap.xml**: ✅ Presente (`{s_name}`)")
            else:
                st.write(f"• **sitemap.xml**: ❌ Ausente")
            ssl_active = all(main_df['URL'].str.startswith('https'))
            st.write(f"• **Certificado SSL**: {'✅ 100% HTTPS' if ssl_active else '⚠️ Contém HTTP'}")

        st.markdown("---")
        
        col_g1, col_g2 = st.columns(2)
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

    # ==========================================
    # --- ABA 2: PLANO DE AÇÃO ---
    # ==========================================
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

    # ==========================================
    # --- ABA 3: DIAGNÓSTICO COM IA ---
    # ==========================================
    with tab_ai:
        st.subheader("🤖 Consultor de SEO & Estratégia de Tráfego com IA")
        st.write("A Inteligência Artificial analisa o Health Score e os problemas técnicos para gerar uma recomendação estratégica:")
        
        top_3_issues = [f"{item[0]} ({item[1]} páginas)" for item in issue_counter.most_common(3)]
        issues_summary_str = ", ".join(top_3_issues) if top_3_issues else "Nenhum problema grave."
        
        prompt_ai = f"""
        Você é um especialista em SEO técnico, marketing de conteúdo e otimização de conversão do SENAI-SP.
        Analise os seguintes dados da auditoria do site {main_domain}:
        - Health Score: {health_score}/100
        - GEO Readiness Score: {geo_score}/100
        - Total de páginas auditadas: {len(main_df)}
        - Principais problemas encontrados: {issues_summary_str}
        - robots.txt: {'Presente' if main_extras.get('has_robots') else 'Ausente'}
        - sitemap.xml: {'Presente' if main_extras.get('has_sitemap') else 'Ausente'}
        - Média de palavras por página: {avg_words}
        - Tempo médio de resposta: {avg_time}s
        
        Gere um parecer executivo contendo:
        1. Diagnóstico Geral do Site (em 2 parágrafos objetivos).
        2. 3 Ações Imediatas de Alto Impacto para ranquear no Google e ser citado por IAs.
        3. Sugestão de Pauta / Palavras-chave estratégicas para aumentar o tráfego orgânico.
        Formate em Markdown limpo com tópicos.
        """
        
        with st.spinner("Gerando diagnóstico estratégico com IA..."):
            diagnostico_ia = generate_text_ai(prompt_ai, "Você é um consultor sênior de SEO do SENAI.")
            
            if not diagnostico_ia:
                diagnostico_ia = f"""### 📊 Parecer Executivo de SEO & GEO • {main_domain}

**1. Diagnóstico Geral:**
O domínio **{main_domain}** obteve um **SEO Health Score de {health_score}/100** e um **GEO Readiness Score de {geo_score}/100**. {'O site apresenta boa estrutura básica, necessitando de refinamento semântico e dados estruturados para maximizar visibilidade.' if health_score >= 70 else 'Foram identificados gargalos importantes que limitam a autoridade no Google e impedem a extração por motores de IA generativa.'}

**2. Ações Prioritárias Recomendadas:**
- **Correção Técnica:** Focar na resolução imediata de *{issues_summary_str}*.
- **Enriquecimento de Conteúdo:** Elevar a média de palavras ({avg_words} palavras atuais) para no mínimo 600 palavras com respostas diretas e dados estatísticos.
- **Indexabilidade para IAs:** {'Garantir submissão do sitemap.xml e liberação de bots de IA no robots.txt.' if not main_extras.get('has_sitemap') else 'Manter sitemap.xml e marcação de Schema.org atualizados.'}

**3. Oportunidades de Tráfego Orgânico & Citação por LLMs:**
- Implementar blocos de respostas diretas nos primeiros parágrafos para capturar snippets do Google e citações no Perplexity/ChatGPT.
- Criar páginas temáticas com dados estruturados (`FAQPage` e `LocalBusiness`).
"""
        st.markdown(diagnostico_ia)

    # ==========================================
    # --- ABA 4: GEO (GENERATIVE ENGINE OPTIMIZATION) ---
    # ==========================================
    with tab_geo_ai:
        st.subheader("⚡ GEO: Generative Engine Optimization")
        st.caption("A nova fronteira do SEO: como otimizar o seu site para ser **citado e recomendado** por motores de busca baseados em IA como **ChatGPT Search, Perplexity, Gemini e Google AI Overviews**.")
        
        col_geo1, col_geo2 = st.columns([1.2, 2])
        with col_geo1:
            st.plotly_chart(render_gauge_score(geo_score, "GEO Readiness Score"), use_container_width=True)
            st.caption("O **GEO Readiness Score** avalia se o seu site possui a densidade de conteúdo, marcação estruturada e permissões de rastreamento necessárias para ser referenciado por IAs generativas.")
        
        with col_geo2:
            st.markdown("#### 🤖 Status dos Rastreadores de IA no `robots.txt`")
            st.write("Verificação em tempo real de permissões para os principais crawlers de Inteligência Artificial:")
            
            ai_bots_data = main_extras.get('ai_bots', {})
            if ai_bots_data:
                cols_b = st.columns(2)
                idx = 0
                for bot_name, bot_info in ai_bots_data.items():
                    with cols_b[idx % 2]:
                        st.markdown(f"""
                        <div style="background-color: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 10px; margin-bottom: 8px;">
                            <div style="font-weight: 600; font-size: 0.95rem; color: #f8fafc;">{bot_info['badge']} {bot_name}</div>
                            <div style="font-size: 0.8rem; color: #94a3b8;">{bot_info['details']['empresa']} • {bot_info['details']['funcao']}</div>
                            <div style="font-size: 0.85rem; color: {'#4ade80' if bot_info['allowed'] else '#f87171'}; margin-top: 4px;">Status: <strong>{bot_info['status']}</strong></div>
                        </div>
                        """, unsafe_allow_html=True)
                    idx += 1
            else:
                st.info("Nenhum arquivo robots.txt encontrado no domínio.")

        st.markdown("---")
        st.markdown("### 🧪 Laboratório Interativo de Conteúdo para GEO")
        st.write("Os motores de IA generativa (como Perplexity e ChatGPT) priorizam parágrafos com **definições diretas (40-60 palavras)**, seguidos de **tópicos numerados/estatísticas** e fontes claras. Teste e otimize qualquer conteúdo abaixo:")

        default_input_text = home_row.get('Snippet_Text', '') if 'home_row' in locals() and home_row.get('Snippet_Text') else "O SENAI São Paulo é referência nacional em educação profissional, tecnologia e inovação industrial, oferecendo cursos técnicos, de qualificação e aperfeiçoamento com alta empregabilidade e laboratórios modernos."
        
        user_raw_content = st.text_area(
            "📝 Texto Original do Site para Análise e Otimização GEO:",
            value=default_input_text,
            height=110
        )

        col_opt1, col_opt2 = st.columns([1, 1])
        with col_opt1:
            btn_geo_optimize = st.button("✨ Otimizar Conteúdo para Citação por IA (GEO)", type="primary", use_container_width=True)
            
        with col_opt2:
            simulate_ia_search = st.button("🔮 Simular Resposta no Perplexity / ChatGPT Search", use_container_width=True)

        if btn_geo_optimize:
            prompt_geo = f"""
            Você é um especialista em GEO (Generative Engine Optimization) e IA de Busca.
            Reescreva o seguinte conteúdo promocional para que ele seja o candidato perfeito para ser citado pelo ChatGPT Search, Perplexity e Google AI Overviews:

            Texto Original:
            "{user_raw_content}"

            Diretrizes de Formatação GEO:
            1. Definição Direta de 40 a 55 palavras no primeiro parágrafo (resposta clara à pergunta 'o que é / o que faz').
            2. Lista com 3 Destaques Técnicos ou Provas Numéricas em bullet points.
            3. 1 Pergunta Frequente (FAQ) curta com resposta direta de 30 palavras.
            4. Código JSON-LD Schema.org 'EducationalOrganization' ou 'Article' compacto.

            Formate em Markdown organizado.
            """
            with st.spinner("Reescrevendo com os pilares de Generative Engine Optimization..."):
                res_geo = generate_text_ai(prompt_geo, "Você é um especialista em GEO e IA Generativa do SENAI-SP.")
                if not res_geo:
                    res_geo = f"""### ⚡ Conteúdo Otimizado para GEO (Generative Engine Optimization)

**1. Definição Direta (Extractable QA):**
O **{main_domain}** é um centro de excelência em formação profissional e tecnologia aplicada, preparando talentos e impulsionando a competitividade industrial por meio de programas práticos, corpo docente altamente qualificado e metodologias alinhadas às demandas reais do mercado de trabalho.

**2. Destaques Técnicos e Métricas:**
* **Infraestrutura Tecnológica:** Laboratórios e oficinas de padrão industrial com equipamentos modernos.
* **Índice de Empregabilidade:** Mais de 80% dos concluintes inseridos diretamente no mercado produtivo.
* **Certificação Oficial:** Diplomas e certificados de prestígio reconhecidos em todo o território nacional.

**3. FAQ Semântico (Para Snippets de IA):**
* **Qual é o diferencial do {main_domain}?**
A metodologia prática focada nas exigências da indústria 4.0, garantindo rápida inserção profissional e desenvolvimento de competências técnicas reais.

**4. Marcação de Dados Estruturados (Schema.org):**
```json
{{
  "@context": "https://schema.org",
  "@type": "EducationalOrganization",
  "name": "{main_domain}",
  "description": "Instituição de ensino profissionalizante e inovação tecnológica industrial."
}}
```
"""
                st.markdown(res_geo)

        if simulate_ia_search:
            st.markdown("#### 💬 Simulação de Resposta no Perplexity / ChatGPT Search")
            st.markdown(f"""
            <div style="background-color: #0f172a; border: 1px solid #38bdf8; border-radius: 10px; padding: 18px; color: #f8fafc; font-family: sans-serif;">
                <div style="font-size: 0.85rem; color: #38bdf8; font-weight: 600; margin-bottom: 8px;">🌐 SÍNTESE DA IA COM CITAÇÃO DIRETA</div>
                <div style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 14px;">
                    Segundo as informações auditadas no portal <strong>{main_domain}</strong>, a instituição se destaca por oferecer capacitação profissional e soluções tecnológicas com alta empregabilidade e metodologia prática de ensino [1].
                </div>
                <div style="display: flex; gap: 8px; align-items: center; background-color: #1e293b; padding: 8px 12px; border-radius: 6px; width: fit-content; border: 1px solid #334155;">
                    <span style="font-size: 0.8rem; color: #94a3b8;">Fonte [1]:</span>
                    <a href="{home_row['URL']}" target="_blank" style="color: #38bdf8; text-decoration: none; font-size: 0.85rem; font-weight: 500;">{main_domain} — Página Principal ↗</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ==========================================
    # --- ABA 5: GEOMARKETING & SEO LOCAL ---
    # ==========================================
    with tab_geomarketing:
        st.subheader("📍 Geomarketing & SEO Local")
        st.caption("Cerca de **46% de todas as buscas no Google** possuem intenção geográfica local (*'perto de mim'*, bairros, cidades). Otimize a presença regional, gere dados estruturados de **LocalBusiness** e simule o alcance por raio em KM.")
        
        geo_sub_tab1, geo_sub_tab2, geo_sub_tab3 = st.tabs([
            "🛠️ Gerador de Schema.org LocalBusiness (JSON-LD)",
            "📋 Checklist de Google Perfil de Empresas & NAP",
            "🎯 Simulador de Raio de Atuação & Conversão Local"
        ])

        with geo_sub_tab1:
            st.markdown("#### 🏢 Gerador de Dados Estruturados `LocalBusiness`")
            st.write("Preencha as informações do negócio para gerar o código JSON-LD padronizado para o Google Maps e Buscas Locais:")
            
            c_lb1, c_lb2 = st.columns(2)
            with c_lb1:
                lb_name = st.text_input("Nome Comercial da Empresa", value="SENAI São Paulo - Unidade Vila Leopoldina")
                lb_type = st.selectbox(
                    "Tipo de Negócio (Schema Type)",
                    ["EducationalOrganization", "LocalBusiness", "Store", "Restaurant", "AutoRepair", "MedicalBusiness", "ProfessionalService"]
                )
                lb_street = st.text_input("Logradouro e Número", value="Rua Jaguaré Mirim, 71")
                lb_neighborhood = st.text_input("Bairro", value="Vila Leopoldina")
                lb_city = st.text_input("Cidade", value="São Paulo")
                lb_state = st.text_input("Estado (UF)", value="SP")
                
            with c_lb2:
                lb_postal = st.text_input("CEP", value="05311-000")
                lb_phone = st.text_input("Telefone / WhatsApp Comercial", value="+55-11-3738-1200")
                lb_url = st.text_input("URL do Site Oficial", value="https://sp.senai.br")
                lb_hours = st.text_input("Horário de Funcionamento (Formato Schema)", value="Mo-Fr 08:00-21:00, Sa 08:00-14:00")
                c_lat, c_lon = st.columns(2)
                with c_lat:
                    lb_lat = st.text_input("Latitude GPS (Opcional)", value="-23.5284")
                with c_lon:
                    lb_lon = st.text_input("Longitude GPS (Opcional)", value="-46.7328")

            # Construção do JSON-LD
            schema_dict = {
                "@context": "https://schema.org",
                "@type": lb_type,
                "name": lb_name,
                "image": f"{lb_url}/logo.png",
                "url": lb_url,
                "telephone": lb_phone,
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": lb_street,
                    "addressLocality": lb_city,
                    "addressRegion": lb_state,
                    "postalCode": lb_postal,
                    "addressCountry": "BR"
                },
                "openingHours": lb_hours
            }
            if lb_lat and lb_lon:
                try:
                    schema_dict["geo"] = {
                        "@type": "GeoCoordinates",
                        "latitude": float(lb_lat),
                        "longitude": float(lb_lon)
                    }
                except ValueError:
                    pass

            schema_json_str = json.dumps(schema_dict, indent=2, ensure_ascii=False)
            schema_html_block = f'<script type="application/ld+json">\n{schema_json_str}\n</script>'

            st.markdown("##### 📄 Código JSON-LD Gerado (Copie e cole dentro da tag `<head>` do seu site):")
            st.code(schema_html_block, language="html")
            st.info("💡 **Dica Pedagógica:** Este código permite que o Google exiba o painel de conhecimento local enriquecido, mapa no Google Maps e botões de 'Ligar' e 'Como Chegar' diretamente na SERP.")

        with geo_sub_tab2:
            st.markdown("#### 📋 Checklist de Consistência NAP & Google Perfil de Empresas (GBP)")
            st.write("A consistência de **NAP** (*Name, Address, Phone*) entre todas as menções na web é o principal fator de ranqueamento no algoritmo de busca local do Google:")
            
            chk1 = st.checkbox("1. Nome da Empresa idêntico no site, Google Meu Negócio, Instagram e CNPJ.", value=True)
            chk2 = st.checkbox("2. Endereço completo com número, complemento e CEP idênticos no rodapé de todas as páginas.", value=True)
            chk3 = st.checkbox("3. Telefone com DDD local ou WhatsApp corporativo fixo e visível.", value=True)
            chk4 = st.checkbox("4. Categoria primária no Google Perfil de Empresas configurada com exatidão.", value=True)
            chk5 = st.checkbox("5. Pelo menos 15 avaliações (Reviews) de clientes com resposta ativa da gerência.", value=False)
            chk6 = st.checkbox("6. Fotos reais da fachada, ambiente interno e equipe em alta resolução adicionadas.", value=True)
            chk7 = st.checkbox("7. Schema `LocalBusiness` implementado no código-fonte da página inicial.", value=False)
            
            nap_score = int((sum([chk1, chk2, chk3, chk4, chk5, chk6, chk7]) / 7) * 100)
            st.metric("Índice de Maturidade em SEO Local", f"{nap_score}%")
            if nap_score >= 80:
                st.success("🌟 Excelente prontidão para dominar as buscas locais da sua região!")
            else:
                st.warning("⚠️ Atenção: complete os itens pendentes do checklist para subir no ranking do Google Maps.")

        with geo_sub_tab3:
            st.markdown("#### 🎯 Simulador de Raio de Atuação e Conversão Local (Geofencing)")
            st.write("Simule o impacto de campanhas de tráfego pago e orgânico regionalizadas por raio geográfico ao redor do ponto físico:")
            
            col_sim1, col_sim2 = st.columns(2)
            with col_sim1:
                radius_km = st.slider("📍 Raio de Atuação Geográfica (KM)", min_value=1, max_value=40, value=5, step=1)
                densidade = st.selectbox("🏙️ Densidade da Região", ["Urbana Densa (ex: Capital/Centro)", "Média Densidade (ex: Bairro Comercial)", "Baixa Densidade (ex: Interior/Rural)"])
                dens_val = 4500 if "Urbana" in densidade else 1800 if "Média" in densidade else 500
                
            with col_sim2:
                verba_local = st.number_input("💰 Orçamento de Mídia Regional (R$ / Mês)", min_value=100.0, max_value=50000.0, value=1500.0, step=100.0)
                ticket_medio = st.number_input("🏷️ Ticket Médio do Produto/Serviço (R$)", min_value=10.0, max_value=10000.0, value=180.0, step=10.0)

            # Cálculo de população e funil
            area_km2 = math.pi * (radius_km ** 2)
            pop_estimada = int(area_km2 * dens_val)
            pop_util = min(pop_estimada, 1500000)
            
            # Campanhas hiperlocais possuem CTR mais elevado
            ctr_local = max(1.5, round(4.5 - (radius_km * 0.08), 2))
            cpc_estimado = round(1.20 + (radius_km * 0.02), 2)
            cliques_estimados = int(verba_local / cpc_estimado)
            visitas_ou_leads = int(cliques_estimados * (ctr_local / 100) * 3.5)
            vendas_estimadas = max(1, int(visitas_ou_leads * 0.18))
            faturamento_estimado = vendas_estimadas * ticket_medio
            roas_local = round(faturamento_estimado / verba_local, 2)

            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("População no Raio", f"{pop_util:,.0f}".replace(",", "."))
            m2.metric("CTR Local Estimado", f"{ctr_local}%")
            m3.metric("Leads / Visitas Locais", f"{visitas_ou_leads}")
            m4.metric("ROAS Regional Estimado", f"{roas_local}x")

            # Gráfico de Funil Local
            fig_funnel_geo = go.Figure(go.Funnel(
                y=["População no Raio", "Alcance Mídia", "Cliques no Anúncio / Mapa", "Visitas Físicas / Leads", "Vendas Fechadas"],
                x=[pop_util, int(verba_local * 8), cliques_estimados, visitas_ou_leads, vendas_estimadas],
                textinfo="value+percent initial",
                marker={"color": ["#38bdf8", "#0284c7", "#0369a1", "#f59e0b", "#10b981"]}
            ))
            fig_funnel_geo.update_layout(title="Funil de Conversão Geográfico (Geofencing)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'), height=350)
            st.plotly_chart(fig_funnel_geo, use_container_width=True)


    # ==========================================
    # --- ABA 6: PALAVRAS-CHAVE & CAUDA LONGA ---
    # ==========================================
    with tab_keywords:
        st.subheader("🔑 Pesquisa de Palavras-Chave & Cauda Longa (SEO & GEO)")
        st.caption("Aprenda a mapear a **intenção de busca do usuário** (*Search Intent*) e explorar termos de **Cauda Longa (Long-Tail)** para vencer a concorrência no Google e ser citado no ChatGPT/Perplexity.")
        
        with st.expander("📖 Entenda: Cauda Curta (*Head Tail*) vs. Cauda Longa (*Long Tail*)", expanded=False):
            st.markdown("""
            * **Head Tail (Cauda Curta):** Termos genéricos (1 a 2 palavras) com altíssimo volume de busca e concorrência gigantesca (ex: *'curso'*, *'marketing'*). Dificuldade alta e conversão baixa.
            * **Middle Tail (Cauda Média):** Termos intermediários (2 a 3 palavras), ex: *'curso de marketing digital'*.
            * **Long Tail (Cauda Longa):** Frases específicas (3 a 6 palavras) que representam a dor exata ou momento de compra do cliente (ex: *'curso de marketing digital com ia aos sábados em sp'*). Menor concorrência e **taxa de conversão até 3x maior**.
            * **GEO Prompts (Busca Conversacional por IA):** Perguntas completas feitas ao ChatGPT, Gemini e Perplexity (ex: *'qual a melhor escola técnica para aprender inteligência artificial no marketing?'*).
            """)

        col_kw1, col_kw2 = st.columns([2, 1])
        with col_kw1:
            kw_product = st.text_input("📦 Produto / Serviço da Empresa:", value="Curso de Marketing Digital com Inteligência Artificial")
            kw_niche = st.text_input("🎯 Nicho / Segmento de Atuação:", value="Educação Profissional & Tecnologia")
        with col_kw2:
            kw_location = st.text_input("📍 Praça / Região Geográfica:", value="São Paulo / Brasil")
            btn_generate_keywords = st.button("✨ Gerar Matriz de Palavras-Chave & Cauda Longa com IA", type="primary", use_container_width=True)

        if btn_generate_keywords or "cached_keywords_matrix" in st.session_state:
            if btn_generate_keywords:
                prompt_kw = f"""
                Você é o maior especialista em SEO, Pesquisa de Palavras-Chave e GEO (Generative Engine Optimization) do SENAI-SP.
                Analise o produto: '{kw_product}', Nicho: '{kw_niche}', Região: '{kw_location}'.

                Gere uma pesquisa estratégica completa estruturada em 3 blocos:
                
                BLOCO 1: MATRIZ DE PALAVRAS-CHAVE (Tabela em Markdown com colunas: Tipo [Head Tail / Middle Tail / Long Tail], Palavra-Chave, Intenção de Busca [Informacional / Comercial / Transacional], Volume Estimado [Alto/Médio/Nicho], Dificuldade de Ranqueamento [Alta/Média/Baixa]). Forneça 6 termos representativos.
                
                BLOCO 2: TOPIC CLUSTERING (Arquitetura de Conteúdo: Defina 1 Pillar Page e 4 Cluster Subtopics recomendados).
                
                BLOCO 3: PROMPTS CONVERSACIONAIS PARA IA (4 perguntas exatas em linguagem natural que usuários fazem no Perplexity e ChatGPT Search sobre este tema).
                """
                with st.spinner("Gerando matriz estratégica de palavras-chave com IA..."):
                    res_kw = generate_text_ai(prompt_kw, "Você é um consultor sênior de SEO e Keyword Research do SENAI-SP.")
                    if not res_kw:
                        res_kw = f"""### 🔑 Matriz Estratégica de Palavras-Chave • {kw_product}

#### 1. Matriz de Classificação por Extensão e Intenção de Busca:
| Tipo | Palavra-Chave | Intenção de Busca | Volume Estimado | Dificuldade |
| :--- | :--- | :--- | :--- | :--- |
| **Head Tail** | marketing digital | Informacional | Altíssimo (>100k/mês) | Muito Alta |
| **Middle Tail** | curso marketing com ia | Comercial | Médio (~5k/mês) | Média |
| **Middle Tail** | ferramentas de ia marketing | Informacional | Médio (~3k/mês) | Média |
| **Long Tail** | curso de marketing digital com ia senai sp | Transacional | Nicho Qualificado | Baixa (Fácil Ranquear) |
| **Long Tail** | como aplicar chatgpt no marketing da empresa | Comercial | Nicho Qualificado | Baixa |
| **Long Tail** | aperfeiçoamento profissional marketing ia 30h | Transacional | Nicho Qualificado | Muito Baixa |

---

#### 2. Agrupamento Semântico (*Topic Clustering* para Pillar Page):
* 🏛️ **Página Pilar (Pillar Page):** *Guia Definitivo de Inteligência Artificial no Marketing Digital (Conceitos, Aplicações e Carreira)*
  * 📑 **Cluster 1:** *Como usar IA para Copywriting e Criação de Conteúdo AIDA/PAS.*
  * 📑 **Cluster 2:** *Mídia Programática e Otimização de Leilão RTB com Machine Learning.*
  * 📑 **Cluster 3:** *Chatbots Inteligentes e Lead Scoring para Atendimento 24/7.*
  * 📑 **Cluster 4:** *Métricas e Análise Preditiva de Vendas com Modelos de IA.*

---

#### 3. Prompts e Perguntas Conversacionais para Motores de IA (GEO):
1. *"Quais são os melhores cursos práticos de marketing digital com inteligência artificial em São Paulo?"*
2. *"Como pequenas empresas podem automatizar o atendimento ao cliente usando chatbots com IA?"*
3. *"Vale a pena fazer o curso de marketing com IA do SENAI para recolocação profissional?"*
4. *"Qual a diferença entre SEO tradicional e GEO na otimização de sites para ChatGPT?"*
"""
                    st.session_state["cached_keywords_matrix"] = res_kw
            
            st.markdown(st.session_state["cached_keywords_matrix"])
            
            # Tabela para download
            df_kw_export = pd.DataFrame([
                {"Tipo": "Head Tail", "Palavra-Chave": f"marketing digital", "Intenção": "Informacional", "Dificuldade": "Alta"},
                {"Tipo": "Middle Tail", "Palavra-Chave": f"curso {kw_product.lower()}", "Intenção": "Comercial", "Dificuldade": "Média"},
                {"Tipo": "Long Tail", "Palavra-Chave": f"onde fazer {kw_product.lower()} em {kw_location.lower()}", "Intenção": "Transacional", "Dificuldade": "Baixa"},
                {"Tipo": "Long Tail", "Palavra-Chave": f"melhor {kw_product.lower()} com certificado", "Intenção": "Transacional", "Dificuldade": "Baixa"},
                {"Tipo": "GEO Prompt", "Palavra-Chave": f"como funciona {kw_product.lower()} na prática", "Intenção": "Informacional/GEO", "Dificuldade": "Nicho"}
            ])
            csv_kw = df_kw_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                "⬇️ Baixar Matriz de Palavras-Chave em CSV",
                data=csv_kw,
                file_name="matriz_palavras_chave_seo_geo.csv",
                mime="text/csv"
            )


    # ==========================================
    # --- ABA 7: AUDITORIA TÉCNICA DETALHADA ---
    # ==========================================
    with tab_tech:
        st.subheader("📄 Tabela Completa de URLs Auditadas")
        st.dataframe(
            main_df[['URL', 'Status Code', 'Response Time', 'Title', 'Word Count', 'H1 Count', 'H2 Count', 'Imagens_Sem_Alt', 'Possui_Schema', 'Possui_OG', 'Problemas_Str']],
            use_container_width=True,
            height=450
        )
        
        csv_data = main_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "⬇️ Baixar Tabela em CSV",
            data=csv_data,
            file_name=f"auditoria_seo_geo_{main_domain}.csv",
            mime="text/csv"
        )

    # ==========================================
    # --- ABA 8: BENCHMARKING COMPETITIVO ---
    # ==========================================
    with tab_comp:
        st.subheader("🏆 Comparativo com Concorrentes")
        if len(full_df['Domínio'].unique()) < 2:
            st.info("💡 Para visualizar o comparativo, insira a URL de ao menos um concorrente na barra lateral e clique em **Iniciar Auditoria Completa**.")
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

    # ==========================================
    # --- EXPORTAR RELATÓRIO COMPLETO EM HTML ---
    # ==========================================
    st.markdown("---")
    st.subheader("📥 Leve seu Relatório de SEO, GEO & Geomarketing para Casa")
    
    top_issues_html = "<ul>" + "".join([f"<li><strong>{item[0]}:</strong> {item[1]} página(s) afetada(s)</li>" for item in issue_counter.most_common(5)]) + "</ul>" if issue_counter else "<p>Nenhum problema grave encontrado.</p>"
    
    secoes_seo = [
        ("1. Sumário Executivo do Site", f"<p><strong>Domínio Auditado:</strong> {main_domain}<br><strong>SEO Health Score:</strong> {health_score}/100<br><strong>GEO Readiness Score (IA Search):</strong> {geo_score}/100<br><strong>Total de Páginas Varridas:</strong> {len(main_df)}<br><strong>robots.txt:</strong> {'Presente' if main_extras.get('has_robots') else 'Ausente'}<br><strong>sitemap.xml:</strong> {'Presente' if main_extras.get('has_sitemap') else 'Ausente'}</p>"),
        ("2. Principais Oportunidades Identificadas", top_issues_html),
        ("3. Diagnóstico e Parecer Estratégico com IA", f"<pre>{diagnostico_ia}</pre>"),
        ("4. Recomendações de GEO (Generative Engine Optimization)", "<p>Implemente blocos de respostas diretas (40-60 palavras), estruture dados em JSON-LD Schema.org e mantenha os rastreadores GPTBot e PerplexityBot permitidos para maximizar citações em LLMs.</p>"),
        ("5. Recomendações de Geomarketing & SEO Local", "<p>Garanta consistência total de NAP (Nome, Endereço e Telefone), mantenha o Google Perfil de Empresas atualizado e incorpore a tag Schema.org/LocalBusiness no cabeçalho do site.</p>")
    ]
    
    html_seo = generate_html_report(
        title=f"Relatório de Auditoria SEO & GEO: {main_domain}",
        subtitle="Diagnóstico de Indexabilidade, Conteúdo, Otimização para IA (GEO) & SEO Local — SENAI-SP",
        sections=secoes_seo
    )
    
    render_download_button(
        label="📥 Baixar Relatório Completo de Auditoria SEO & GEO em HTML",
        data=html_seo,
        file_name=f"auditoria_seo_geo_{main_domain}.html",
        mime="text/html"
    )

else:
    st.info("👆 Configure a URL do site no painel acima e clique em **🚀 Iniciar Auditoria Completa de SEO, GEO & Local** para varrer o site e gerar os diagnósticos.")
    
    # Seção introdutória didática enquanto o aluno não roda o crawler
    st.markdown("### 📚 O que você pode auditar e aprender neste módulo:")
    col_intro1, col_intro2, col_intro3 = st.columns(3)
    
    with col_intro1:
        st.markdown("""
        <div style="background-color: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 16px; height: 100%;">
            <h4>🔍 1. SEO Tradicional</h4>
            <p style="font-size: 0.9rem; color: #94a3b8;">
                Varrer tags On-Page (Title, H1, Meta Description, Alt Text, Canonical), sitemap.xml, robots.txt e cálculo de Health Score de indexabilidade.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_intro2:
        st.markdown("""
        <div style="background-color: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 16px; height: 100%;">
            <h4>⚡ 2. GEO (IA Search)</h4>
            <p style="font-size: 0.9rem; color: #94a3b8;">
                <em>Generative Engine Optimization</em>: Otimize conteúdos para serem citados como fonte no <strong>ChatGPT Search, Perplexity, Gemini e Google AI Overviews</strong>.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_intro3:
        st.markdown("""
        <div style="background-color: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 16px; height: 100%;">
            <h4>📍 3. Geomarketing & Local</h4>
            <p style="font-size: 0.9rem; color: #94a3b8;">
                Gerador de <strong>Schema.org LocalBusiness</strong> (JSON-LD), checklist de Google Meu Negócio / NAP e simulação de conversão por raio de KM.
            </p>
        </div>
        """, unsafe_allow_html=True)

render_sidebar_footer()
render_academic_footer()

import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import pandas as pd
from utils.auth import check_authentication
from utils.ai_helper import render_api_key_sidebar
from utils.export_helper import generate_html_report, render_download_button
from utils.ui_components import render_sidebar_header, render_sidebar_footer, render_academic_footer

st.set_page_config(page_title="Recomendação & Neuromarketing | SENAI", page_icon="🛍️", layout="wide")
render_sidebar_header()
check_authentication()
render_api_key_sidebar()

st.title("🛍️ Motor de Recomendação & Laboratório de Neuromarketing")
st.caption("Alinhado ao **Módulo 4 da Ementa SENAI**: Experiência do cliente, sistemas de recomendação de produtos/serviços, personalização e neuromarketing.")

# Catálogo Didático de Produtos
CATALOGO = [
    {"id": 1, "nome": "Curso Especialista em IA para Negócios", "cat": "Cursos", "preco_original": 790.0, "preco_promo": 490.0, "tags": ["ia", "gestao", "tecnologia"], "compras_juntas": [3, 4], "vendas_dia": 42},
    {"id": 2, "nome": "Mentoria 1-on-1 de Carreira Tech", "cat": "Serviços", "preco_original": 1200.0, "preco_promo": 890.0, "tags": ["carreira", "tecnologia", "consultoria"], "compras_juntas": [1], "vendas_dia": 15},
    {"id": 3, "nome": "Kit de Automação de Marketing & CRM", "cat": "Software", "preco_original": 350.0, "preco_promo": 240.0, "tags": ["ia", "automacao", "vendas"], "compras_juntas": [1, 5], "vendas_dia": 68},
    {"id": 4, "nome": "Certificação Internacional em Prompt Engineering", "cat": "Cursos", "preco_original": 550.0, "preco_promo": 390.0, "tags": ["ia", "prompts", "tecnologia"], "compras_juntas": [1], "vendas_dia": 31},
    {"id": 5, "nome": "E-book: 50 Prompts Práticos para Vendas", "cat": "Conteúdo", "preco_original": 97.0, "preco_promo": 47.0, "tags": ["vendas", "prompts", "conteudo"], "compras_juntas": [3], "vendas_dia": 120},
    {"id": 6, "nome": "Auditoria de Campanhas e SEO com IA", "cat": "Serviços", "preco_original": 1500.0, "preco_promo": 1100.0, "tags": ["gestao", "seo", "consultoria"], "compras_juntas": [3], "vendas_dia": 9}
]

col_config, col_store = st.columns([1, 2], gap="large")

with col_config:
    st.subheader("👤 1. Perfil do Cliente Simulado")
    perfil = st.selectbox(
        "Selecione o Comportamento do Usuário:",
        [
            "Aluno Interessado em Inteligência Artificial e Negócios (Navegando em Cursos)",
            "Gestor de Vendas buscando Automação e Ferramentas",
            "Profissional buscando Transição de Carreira e Mentoria",
            "Novo Visitante (Sem Histórico Prévio)"
        ]
    )
    
    st.markdown("---")
    st.subheader("🧠 2. Algoritmo de Recomendação")
    algoritmo = st.radio(
        "Escolha o Motor de Personalização:",
        [
            "Filtragem Baseada em Conteúdo (Similaridade de Atributos/Tags)",
            "Filtragem Colaborativa ('Quem comprou X também comprou Y')",
            "Padrão Sem IA (Ordem Cronológica / Aleatória)"
        ]
    )
    
    st.markdown("---")
    st.subheader("⚡ 3. Gatilhos de Neuromarketing")
    st.write("Ative os gatilhos psicológicos na interface:")
    g_escassez = st.checkbox("🏷️ **Escassez:** Exibir estoque baixo ('Restam 2 vagas!')", value=True)
    g_urgencia = st.checkbox("⏳ **Urgência:** Cronômetro regressivo de oferta relâmpago", value=True)
    g_social = st.checkbox("👥 **Prova Social:** Contagem de pessoas comprando ao vivo", value=True)
    g_ancoragem = st.checkbox("⚓ **Ancoragem de Preço:** Mostrar preço 'De R$ X por R$ Y'", value=True)

# Lógica de Ordenação e Recomendação por IA
produtos_exibidos = CATALOGO.copy()

if "Filtragem Baseada em Conteúdo" in algoritmo:
    if "Inteligência Artificial" in perfil:
        produtos_exibidos.sort(key=lambda x: ("ia" in x["tags"], "tecnologia" in x["tags"]), reverse=True)
    elif "Gestor de Vendas" in perfil:
        produtos_exibidos.sort(key=lambda x: ("automacao" in x["tags"], "vendas" in x["tags"]), reverse=True)
    elif "Transição de Carreira" in perfil:
        produtos_exibidos.sort(key=lambda x: ("carreira" in x["tags"], "consultoria" in x["tags"]), reverse=True)

elif "Filtragem Colaborativa" in algoritmo:
    if "Inteligência Artificial" in perfil:
        itens_prioritarios = [1, 4, 3, 2, 5, 6]
    elif "Gestor de Vendas" in perfil:
        itens_prioritarios = [3, 5, 1, 6, 4, 2]
    elif "Transição de Carreira" in perfil:
        itens_prioritarios = [2, 1, 4, 6, 3, 5]
    else:
        itens_prioritarios = [1, 2, 3, 4, 5, 6]
    produtos_exibidos.sort(key=lambda x: itens_prioritarios.index(x["id"]))

# Cálculo do impacto na taxa de conversão simulada
cvr_base = 1.8
if "Filtragem" in algoritmo:
    cvr_base += 1.4
if g_escassez:
    cvr_base += 0.6
if g_urgencia:
    cvr_base += 0.5
if g_social:
    cvr_base += 0.7
if g_ancoragem:
    cvr_base += 0.8

with col_store:
    st.subheader("🛒 Vitrine Personalizada da Loja / Portal")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Taxa de Conversão Prevista", f"{cvr_base:.1f}%", f"+{cvr_base - 1.8:.1f}% com Otimizações")
    m2.metric("Aumento no Ticket Médio", "+28%", "Cross-sell Inteligente")
    m3.metric("Engajamento da Sessão", "+42%", "Relevância de Conteúdo")
    
    if g_urgencia:
        st.warning("🔥 **OFERTA ESPECIAL DA TURMA SENAI:** Os descontos abaixo encerram em **04:59 minutos**!")
        
    st.write("")
    
    cols_grid = st.columns(2)
    for idx, prod in enumerate(produtos_exibidos[:4]):
        with cols_grid[idx % 2]:
            with st.container(border=True):
                st.markdown(f"**{prod['nome']}**")
                st.caption(f"Categoria: `{prod['cat']}` • Tags: `{', '.join(prod['tags'])}`")
                
                if g_ancoragem:
                    st.markdown(f"<span style='text-decoration: line-through; color: #94a3b8;'>De R$ {prod['preco_original']:.2f}</span> por <strong style='font-size: 1.3rem; color: #38bdf8;'>R$ {prod['preco_promo']:.2f}</strong>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<strong style='font-size: 1.3rem; color: #38bdf8;'>R$ {prod['preco_promo']:.2f}</strong>", unsafe_allow_html=True)
                
                if g_social:
                    st.caption(f"👥 **{prod['vendas_dia']} pessoas** se matricularam hoje nas últimas horas.")
                    
                if g_escassez:
                    st.error("⚠️ Restam apenas **3 vagas/licenças** com este valor.")
                    
                if st.button("Comprar / Simular Clique 🛒", key=f"btn_buy_{prod['id']}", use_container_width=True):
                    st.balloons()
                    st.success(f"🎉 Conversão registrada com sucesso para o item '{prod['nome']}'!")

    st.markdown("---")
    secoes_ux = [
        ("1. Diagnóstico de Personalização de UX", f"<p><strong>Perfil Testado:</strong> {perfil}<br><strong>Algoritmo Selecionado:</strong> {algoritmo}</p>"),
        ("2. Gatilhos de Neuromarketing Ativados", f"<ul><li>Escassez: {'Ativo' if g_escassez else 'Inativo'}</li><li>Urgência: {'Ativo' if g_urgencia else 'Inativo'}</li><li>Prova Social: {'Ativo' if g_social else 'Inativo'}</li><li>Ancoragem de Preço: {'Ativo' if g_ancoragem else 'Inativo'}</li></ul>"),
        ("3. Impacto Estimado nas Vendas", f"<p>A taxa de conversão saltou de <strong>1.8% (base)</strong> para <strong>{cvr_base:.1f}%</strong> com a combinação de algoritmos de recomendação e gatilhos cognitivos.</p>")
    ]
    
    html_ux = generate_html_report(
        title="Auditoria de Personalização & Neuromarketing",
        subtitle="Laboratório de Experiência do Cliente - SENAI",
        sections=secoes_ux
    )
    
    render_download_button(
        label="📥 Baixar Análise de UX & Neuromarketing em HTML",
        data=html_ux,
        file_name="analise_ux_neuromarketing_ia.html",
        mime="text/html"
    )

render_sidebar_footer()
render_academic_footer()

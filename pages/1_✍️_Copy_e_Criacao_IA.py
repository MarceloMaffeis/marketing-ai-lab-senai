import streamlit as st
from utils.auth import check_authentication
from utils.ai_helper import render_api_key_sidebar, generate_text_ai, generate_copy_offline, analyze_ethics_offline
from utils.export_helper import generate_html_report, render_download_button

st.set_page_config(page_title="Copywriting & Criação com IA | SENAI", page_icon="✍️", layout="wide")
check_authentication()
render_api_key_sidebar()

st.title("✍️ Estúdio de Copywriting, Criativos & Ética com IA")
st.caption("Alinhado ao **Módulo 5 da Ementa SENAI**: Técnicas de copywriting, criação visual, automação e ética no uso da IA.")

st.markdown("---")

col_form, col_result = st.columns([1, 1], gap="large")

with col_form:
    st.subheader("📋 Configuração da Campanha")
    
    produto = st.text_input("1. Produto ou Serviço:", value="Curso de Manutenção de Drones Industriais", placeholder="Ex: Curso de Marketing, Tênis de Corrida, Software...")
    publico = st.text_input("2. Público-Alvo / Persona:", value="Técnicos em eletrônica e engenheiros em busca de recolocação", placeholder="Ex: Jovens universitários, Donos de pequenas empresas...")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        objetivo = st.selectbox("3. Objetivo Principal:", ["Venda Direta / Matrícula", "Geração de Leads (Cadastro)", "Reconhecimento de Marca", "Engajamento"])
        framework = st.selectbox("4. Framework de Copy:", ["AIDA (Atenção, Interesse, Desejo, Ação)", "PAS (Problema, Agitação, Solução)"])
    with col_f2:
        tom = st.selectbox("5. Tom de Voz:", ["Persuasivo & Enérgico", "Profissional & Técnico", "Descontraído & Jovem", "Inspirador & Emocional"])
        formato = st.selectbox("6. Formato do Anúncio:", ["Post Feed Instagram (Carrossel)", "Story / Reels (Script)", "Anúncio Meta Ads (Feed)", "Google Ads (Texto)"])
    
    beneficio_chave = st.text_area("7. Diferencial Competitivo / Proposta de Valor:", value="Aulas 100% práticas em laboratório, certificado reconhecido nacionalmente e suporte para empreender.", height=80)
    
    btn_gerar = st.button("✨ Gerar Campanha & Analisar com IA", type="primary", use_container_width=True)

# Processamento e exibição de resultados
if btn_gerar:
    with col_result:
        st.subheader("🚀 Resultados Gerados")
        
        with st.spinner("A Inteligência Artificial está estruturando o criativo..."):
            fw_tipo = "AIDA" if "AIDA" in framework else "PAS"
            
            # Prompt para LLM (caso API key esteja presente)
            system_prompt = (
                "Você é um especialista sênior em Marketing Digital, Copywriting e Publicidade com Inteligência Artificial. "
                "Responda sempre em português claro, profissional e persuasivo, formatado em Markdown."
            )
            user_prompt = f"""
            Crie uma copy de alta conversão para o seguinte produto:
            - Produto: {produto}
            - Público-Alvo: {publico}
            - Objetivo: {objetivo}
            - Framework: {fw_tipo}
            - Tom de Voz: {tom}
            - Formato: {formato}
            - Diferencial: {beneficio_chave}
            
            Retorne:
            1. Copy completa estruturada exatamente nas etapas do framework ({fw_tipo}).
            2. Sugestão de 3 títulos (headlines) para teste A/B.
            3. Prompt detalhado em inglês para gerar a imagem publicitária em ferramentas como Midjourney/DALL-E.
            4. Hashtags recomendadas.
            """
            
            texto_ia = generate_text_ai(user_prompt, system_prompt)
            
            # Se não houver LLM conectada, usa o gerador estruturado offline
            if not texto_ia:
                copy_dados = generate_copy_offline(produto, publico, objetivo, tom, fw_tipo)
                
                if fw_tipo == "AIDA":
                    copy_formatada = f"""### 📢 Copywriting Estruturado ({fw_tipo})
- **[A] Atenção:** {copy_dados['atencao']}
- **[I] Interesse:** {copy_dados['interesse']}
- **[D] Desejo:** {copy_dados['desejo']} (Diferencial: *{beneficio_chave}*)
- **[A] Ação (CTA):** {copy_dados['acao']}

---
### 🧪 Variações de Títulos (Headlines para Teste A/B):
1. **Opção 1 (Benefício):** *Domine {produto} e destaque-se no mercado agora!*
2. **Opção 2 (Curiosidade):** *O segredo que {publico} está usando para {objetivo.lower()}.*
3. **Opção 3 (Urgência):** *Últimas vagas para acelerar sua carreira em {produto}.*

---
### 🎨 Prompt Visual para IA Generativa (Midjourney / DALL-E / Canva):
`A photorealistic cinematic shot of {produto.lower()} in a modern high-tech workshop, used by an energetic professional ({publico.lower()}), volumetric lighting, 8k resolution, professional commercial photography, dynamic depth of field --ar 1:1`

---
### 🏷️ Hashtags Sugeridas:
{copy_dados['hashtags']}
"""
                else:
                    copy_formatada = f"""### 📢 Copywriting Estruturado ({fw_tipo})
- **[P] Problema:** {copy_dados['problema']}
- **[A] Agitação:** {copy_dados['agitacao']}
- **[S] Solução:** {copy_dados['solucao']} (Destaque: *{beneficio_chave}*)
- **[A] Ação (CTA):** {copy_dados['acao']}

---
### 🧪 Variações de Títulos (Headlines para Teste A/B):
1. **Opção 1 (Dor):** *Cansado de perder oportunidades em {produto}?*
2. **Opção 2 (Transformação):** *Como {publico} está alcançando {objetivo.lower()} em tempo recorde.*
3. **Opção 3 (Solução):** *A tecnologia definitiva para transformar seus resultados.*

---
### 🎨 Prompt Visual para IA Generativa (Midjourney / DALL-E / Canva):
`An inspiring modern studio photograph showing the real solution of {produto.lower()} applied to {publico.lower()}, clean minimalist background, vibrant colors, premium advertising aesthetic --ar 1:1`

---
### 🏷️ Hashtags Sugeridas:
{copy_dados['hashtags']}
"""
            else:
                copy_formatada = texto_ia

            # Exibe a copy formatada
            st.markdown(copy_formatada)
            
            # Análise de Ética e LGPD
            st.markdown("---")
            st.subheader("🛡️ Scanner de Ética, LGPD & Boas Práticas")
            analise_etica = analyze_ethics_offline(copy_formatada)
            
            col_e1, col_e2 = st.columns([1, 3])
            with col_e1:
                st.metric("Índice de Conformidade", f"{analise_etica['score']}%", analise_etica['nivel'])
            with col_e2:
                for alerta in analise_etica['alertas']:
                    st.write(alerta)
            
            # Exportação de Relatório para Levar para Casa
            st.markdown("---")
            st.subheader("📥 Leve seu Projeto para Casa")
            
            relatorio_secoes = [
                ("1. Informações da Campanha", f"<p><strong>Produto:</strong> {produto}<br><strong>Público:</strong> {publico}<br><strong>Objetivo:</strong> {objetivo}<br><strong>Framework:</strong> {fw_tipo}</p>"),
                ("2. Conteúdo Gerado pela IA", f"<pre>{copy_formatada}</pre>"),
                ("3. Auditoria de Ética e LGPD", f"<p><strong>Conformidade:</strong> {analise_etica['score']}% ({analise_etica['nivel']})</p><ul>" + "".join([f"<li>{a}</li>" for a in analise_etica['alertas']]) + "</ul>")
            ]
            
            html_content = generate_html_report(
                title=f"Plano de Conteúdo: {produto}",
                subtitle=f"Criado por Inteligência Artificial • Framework {fw_tipo}",
                sections=relatorio_secoes
            )
            
            render_download_button(
                label="📥 Baixar Relatório Completo da Campanha (.HTML)",
                data=html_content,
                file_name=f"plano_campanha_{produto.replace(' ', '_').lower()}.html",
                mime="text/html"
            )
else:
    with col_result:
        st.info("👈 Preencha os campos ao lado e clique em **Gerar Campanha & Analisar com IA** para visualizar a copy estruturada, os prompts visuais e a auditoria de conformidade.")

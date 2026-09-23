---
title: Marketing AI Lab SENAI
emoji: 🚀
colorFrom: red
colorTo: blue
sdk: streamlit
sdk_version: 1.35.0
app_file: app.py
pinned: false
license: mit
---

# 🚀 Marketing AI Lab — SENAI

Ambiente integrado de ferramentas práticas e simuladores de **Inteligência Artificial aplicada ao Marketing Digital**, desenvolvido sob medida para a matriz curricular do curso de **Aperfeiçoamento Profissional (30h)** do SENAI-SP.

---

## 🎯 Mapeamento das Ferramentas com a Ementa SENAI

| Ferramenta / Módulo | Ementa SENAI | O que o Aluno Pratica |
| :--- | :--- | :--- |
| **🔍 1. Auditoria SEO, GEO & Palavras-Chave** | **Módulo 1:** Fundamentos, Tráfego Orgânico & SEO | Diagnóstico On-Page, otimização para IA (ChatGPT/Perplexity), Schema LocalBusiness e Matriz de Palavras-Chave de Cauda Longa. |
| **🤖 2. Construtor de Chatbot & Leads** | **Módulo 1:** Automação e assistentes virtuais | Configuração de personas de IA, atendimento 24/7, contorno de objeções e termômetro de *Lead Scoring*. |
| **📈 3. Matriz de Métricas & Calculadora de KPIs** | **Módulo 2:** Análise de dados e indicadores | Dicionário dos 18 KPIs fundamentais de marketing, simulador interativo de fórmulas e metas SMART com IA. |
| **🎯 4. Simulador de Mídia Programática** | **Módulo 3:** Publicidade programática e IA | Simulação de leilão RTB em tempo real, Smart Bidding vs. Lance Manual, funil de conversão e ROAS. |
| **🛍️ 5. Recomendação & Neuromarketing** | **Módulo 4:** Experiência do cliente & Personalização | Vitrine inteligente com filtragem colaborativa/conteúdo e ativação de 4 gatilhos mentais cognitivos. |
| **✍️ 6. Copywriting & Criativos com IA** | **Módulo 5:** Criação de conteúdos & Ética | Aplicação de frameworks AIDA/PAS, prompts para DALL-E/Midjourney e auditoria de conformidade LGPD. |
| **📊 7. Dashboard de BI & Previsão Preditiva** | **Módulo 6:** Tomada de decisão com dados & ML | Análise de dados de campanhas e projeção de faturamento com regressão linear (Scikit-Learn). |

---

## 💻 Como Rodar Localmente no seu Computador

1. Abra o terminal na pasta do projeto:
```bash
cd marketing_ai_lab
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o aplicativo:
```bash
streamlit run app.py
```

4. O sistema abrirá automaticamente no seu navegador em `http://localhost:8501`.
   * **Senha padrão de acesso:** `senai`

---

## 🤗 Como Fazer o Deploy Gratuito no Hugging Face Spaces (Ideal para Redes SENAI / UNIP)

O **Hugging Face** é o principal hub global de Inteligência Artificial e **não é bloqueado pelos firewalls do SENAI, UNIP e universidades**:

1. Crie uma conta gratuita em [huggingface.co](https://huggingface.co/).
2. No menu superior direito, clique na sua foto de perfil ➔ **"New Space"**.
3. Preencha as configurações:
   * **Space name:** `marketing-ai-lab` (ou o nome que preferir)
   * **License:** `mit`
   * **Select the Space SDK:** Escolha **Streamlit**
   * **Space hardware:** **CPU basic • 2 vCPU • 16GB (Free)**
   * **Privacy:** **Public**
4. Escolha como subir o código:
   * **Opção Direta pelo GitHub:** Conecte seu repositório `marketing-ai-lab-senai`.
   * **Ou via Upload de Arquivos:** Suba os arquivos desta pasta diretamente no navegador.
5. Em **Settings ➔ Variables and secrets**, você pode adicionar:
   * `CLASS_PASSWORD` = `senai`
   * `GEMINI_API_KEY` = `sua_chave_do_google_ai_studio`
6. Pronto! O Hugging Face construirá o app automaticamente e fornecerá um link público direto (ex: `https://huggingface.co/spaces/seu-usuario/marketing-ai-lab`).

---

## ☁️ Como Fazer o Deploy no Streamlit Cloud

1. Suba esta pasta para um repositório no seu **GitHub** (ex: `marketing-ai-lab-senai`).
2. Acesse [share.streamlit.io](https://share.streamlit.io) e faça login com sua conta do GitHub.
3. Clique em **"New App"** e selecione o seu repositório.
4. Defina o **Main file path:** `app.py`.
5. Clique em **"Deploy!"**. Em menos de 2 minutos seu link `https://seu-app.streamlit.app` estará online!

---

## 📥 Como os Alunos Levam os Projetos para Casa

* Em todas as páginas há um botão **"📥 Baixar Relatório em HTML"**.
* O arquivo gerado é um relatório com design profissional pronto para o aluno abrir em qualquer navegador, imprimir em PDF ou adicionar ao seu portfólio profissional!

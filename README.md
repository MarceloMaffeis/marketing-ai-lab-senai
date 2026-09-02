# 🚀 Marketing AI Lab — SENAI

Ambiente integrado de ferramentas práticas e simuladores de **Inteligência Artificial aplicada ao Marketing Digital**, desenvolvido sob medida para a matriz curricular do curso de **Aperfeiçoamento Profissional (30h)** do SENAI-SP.

---

## 🎯 Mapeamento das Ferramentas com a Ementa SENAI

| Ferramenta / Módulo | Ementa SENAI | O que o Aluno Pratica |
| :--- | :--- | :--- |
| **✍️ 1. Copywriting & Criativos com IA** | **Módulo 5:** Criação de conteúdos, Copywriting & Ética | Aplicação de frameworks AIDA/PAS, prompts para DALL-E/Midjourney e auditoria de ética e LGPD. |
| **🎯 2. Simulador de Mídia Programática** | **Módulo 3:** Publicidade programática e IA | Simulação de leilão RTB em tempo real, Smart Bidding vs. Lance Manual, CTR, CPA e ROAS. |
| **🛍️ 3. Recomendação & Neuromarketing** | **Módulo 4:** Experiência do cliente & Personalização | Vitrine inteligente com filtragem baseada em conteúdo/colaborativa e ativação de gatilhos mentais. |
| **📊 4. Dashboard de BI & Previsão Preditiva** | **Módulos 2 e 6:** Análise de dados, ML & KPIs | Análise de métricas reais de Meta/Google Ads e projeção de receita com Machine Learning (Scikit-Learn). |
| **🤖 5. Construtor de Chatbot & Leads** | **Módulo 1:** Automação e assistentes virtuais | Configuração de personas de IA, atendimento 24/7, extração de contatos e termômetro de *Lead Scoring*. |

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

## ☁️ Como Fazer o Deploy Gratuito na Nuvem (Streamlit Cloud)

Para que todos os seus alunos acessem pelo celular ou computador de qualquer lugar:

1. Suba esta pasta para um repositório no seu **GitHub** (ex: `marketing-ai-lab-senai`).
2. Acesse [share.streamlit.io](https://share.streamlit.io) e faça login com sua conta do GitHub.
3. Clique em **"New App"** e selecione o seu repositório.
4. Defina:
   * **Main file path:** `app.py`
5. *(Opcional)* Em **Advanced settings -> Secrets**, você pode configurar:
```toml
CLASS_PASSWORD = "sua_senha_da_turma"
GEMINI_API_KEY = "sua_chave_do_google_ai_studio"
```
6. Clique em **"Deploy!"**. Em menos de 2 minutos seu link `https://seu-nome-app.streamlit.app` estará online!

---

## 📥 Como os Alunos Levam os Projetos para Casa

* Em cada página há um botão **"📥 Baixar Relatório em HTML"**.
* O arquivo gerado é um relatório com design profissional pronto para o aluno abrir em qualquer navegador, imprimir em PDF ou adicionar ao seu portfólio profissional!

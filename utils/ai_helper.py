import os
import streamlit as st

def get_api_key():
    """Recupera a chave de API da sessão, secrets ou variáveis de ambiente de forma segura."""
    if "user_gemini_key" in st.session_state and st.session_state["user_gemini_key"]:
        return st.session_state["user_gemini_key"].strip()
    
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            return str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        pass
        
    return os.getenv("GEMINI_API_KEY", "")

def render_api_key_sidebar():
    """Renderiza um campo opcional na barra lateral para o aluno/professor inserir a chave."""
    with st.sidebar.expander("🔑 Configurar Chave de IA (Opcional)", expanded=False):
        current_key = get_api_key()
        user_key = st.text_input(
            "Google Gemini API Key:",
            value=st.session_state.get("user_gemini_key", ""),
            type="password",
            placeholder="AIzaSy...",
            help="Insira sua chave gratuita do Google AI Studio se quiser respostas dinâmicas em tempo real. Se deixar em branco, o sistema usará o motor inteligente offline."
        )
        if user_key != st.session_state.get("user_gemini_key", ""):
            st.session_state["user_gemini_key"] = user_key
            st.rerun()

        if current_key:
            st.caption("✅ Motor de IA Conectado: **Google Gemini Ativo**")
        else:
            st.caption("⚡ Motor Ativo: **Simulador Inteligente Integrado (Sem Custo)**")

def generate_text_ai(prompt: str, system_instruction: str = "") -> str:
    """
    Gera texto usando a API do Gemini se disponível; caso contrário, executa fallback inteligente.
    """
    api_key = get_api_key()
    
    if api_key:
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=api_key)
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                )
            )
            if response and response.text:
                return response.text
        except Exception as e:
            st.warning(f"⚠️ Erro ao consultar a API do Gemini ({str(e)}). Usando o gerador inteligente integrado.")

    # Fallback inteligente se não houver chave ou se ocorrer erro na API
    return None

def generate_copy_offline(produto: str, publico: str, objetivo: str, tom: str, framework: str) -> dict:
    """Gera copies completas e estruturadas usando templates heurísticos ricos."""
    if framework == "AIDA":
        return {
            "atencao": f"🚨 Descubra como revolucionar seus resultados em {produto}! Você ainda perde tempo com métodos tradicionais?",
            "interesse": f"Desenvolvido especificamente para {publico}, nossa solução une tecnologia de ponta e praticidade para atender seu foco em {objetivo.lower()}.",
            "desejo": f"Imagine alcançar seus objetivos com agilidade, sem frustração e com o dobro de eficiência comprovada pelo mercado.",
            "acao": f"👉 Clique no link agora e garanta uma demonstração exclusiva com condições especiais para {publico}!",
            "hashtags": f"#{produto.replace(' ', '')} #Inovação #MarketingDigital #{publico.split()[0]} #ResultadosReais"
        }
    else: # PAS
        return {
            "problema": f"❌ Você, que atua como {publico}, sabe como é exaustivo tentar atingir {objetivo.lower()} sem as ferramentas certas.",
            "agitacao": f"Cada dia adiando a mudança custa tempo, dinheiro e clientes que estão migrando para concorrentes mais ágeis.",
            "solucao": f"💡 Conheça {produto}: a resposta definitiva para automatizar processos, maximizar o retorno e colocar você na liderança.",
            "acao": f"🚀 Transforme sua realidade hoje mesmo. Toque no botão e comece sem compromisso!",
            "hashtags": f"#SolucaoInteligente #{produto.replace(' ', '')} #AltaPerformance #Estrategia"
        }

def analyze_ethics_offline(copy_text: str) -> dict:
    """Analisa conformidade ética, transparência e possíveis riscos legais/LGPD."""
    palavras_risco = ["garantido", "100%", "milagre", "fique rico", "sem esforço", "lucro certo", "dados pessoais", "vitalício grátis"]
    encontradas = [w for w in palavras_risco if w in copy_text.lower()]
    
    score = 100 - (len(encontradas) * 20)
    score = max(score, 30)
    
    alertas = []
    if encontradas:
        alertas.append(f"⚠️ Termos de alto risco ou promessas exageradas detectados: `{', '.join(encontradas)}`. No Brasil, o CONAR e o CDC proíbem promessas absolutas que não possam ser comprovadas.")
    else:
        alertas.append("✅ Nenhuma promessa exagerada explícita detectada.")
        
    alertas.append("✅ **Adequação à LGPD:** Se coletar leads (nome, e-mail, WhatsApp), certifique-se de incluir checkbox explícito de consentimento e link para a Política de Privacidade.")
    alertas.append("ℹ️ **Transparência de IA:** É uma boa prática informar aos usuários quando um atendimento ou conteúdo foi assistido por Inteligência Artificial.")
    
    return {
        "score": score,
        "nivel": "Excelente" if score >= 85 else "Atenção Necessária" if score >= 60 else "Alto Risco",
        "alertas": alertas
    }

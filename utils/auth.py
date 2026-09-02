import streamlit as st

DEFAULT_PASSWORD = "senai"

def get_class_password():
    """Recupera a senha da turma com fallback seguro caso o secrets.toml não exista."""
    try:
        if hasattr(st, "secrets") and "CLASS_PASSWORD" in st.secrets:
            return str(st.secrets["CLASS_PASSWORD"]).strip()
    except Exception:
        pass
    return DEFAULT_PASSWORD

def check_authentication():
    """
    Verifica se o usuário está autenticado na sessão.
    Se não estiver, renderiza o formulário de login e interrompe a execução da página.
    """
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        # Renderiza no topo da sidebar o status logado
        with st.sidebar:
            st.success("🟢 Acesso liberado (Turma Ativa)")
            if st.button("Sair / Bloquear", key="logout_btn", use_container_width=True):
                st.session_state["authenticated"] = False
                st.rerun()
        return True

    # Tela de Login amigável para os alunos
    st.markdown(
        """
        <style>
        .login-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            padding: 2.5rem;
            border-radius: 16px;
            border: 1px solid #334155;
            color: #f8fafc;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        }
        .login-badge {
            display: inline-block;
            background: #e11d48;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: bold;
            margin-bottom: 12px;
        }
        </style>
        <div class="login-card">
            <span class="login-badge">SENAI - Gestão & Negócios</span>
            <h2>🎓 Marketing Digital com IA - Lab</h2>
            <p>Ambiente prático integrado de simulação e ferramentas de Inteligência Artificial aplicada ao Marketing.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔐 Acesso da Turma")
        expected_password = get_class_password()

        senha_digitada = st.text_input(
            "Digite a senha fornecida pelo instrutor:",
            type="password",
            placeholder="Ex: senai",
            key="input_turma_password"
        )

        if st.button("Entrar no Hub do Curso 🚀", use_container_width=True, type="primary"):
            if senha_digitada.strip().lower() == str(expected_password).strip().lower():
                st.session_state["authenticated"] = True
                st.success("Acesso autorizado! Carregando ferramentas...")
                st.rerun()
            else:
                st.error("❌ Senha incorreta. Consulte o instrutor da turma.")

        st.info("💡 **Dica para o instrutor:** A senha padrão de demonstração é `senai`.")

    st.stop()

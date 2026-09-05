import streamlit as st

def render_sidebar_header():
    """Renderiza o cabeçalho padrão na barra lateral."""
    st.sidebar.markdown(
        """
        <div style="margin-bottom: 1rem;">
            <h2 style="margin: 0; font-size: 1.5rem; font-weight: 800; color: #f8fafc;">
                🚀 Marketing AI Lab
            </h2>
            <p style="margin: 0; font-size: 0.85rem; color: #94a3b8;">
                Plataforma Didática de IA para Marketing Digital
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_sidebar_footer():
    """Renderiza o rodapé institucional na barra lateral com licença MIT."""
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style="font-size: 0.8rem; color: #94a3b8; line-height: 1.5;">
            <p style="margin-bottom: 4px;">📜 <strong>Código Aberto sob Licença MIT</strong></p>
            <p style="margin: 0;">SENAI-SP — Formação Inicial e Continuada</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_academic_footer():
    """Renderiza o rodapé acadêmico, licença MIT e o aviso legal (disclaimer)."""
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; margin-top: 2rem; margin-bottom: 1.5rem;">
            <p style="font-size: 0.95rem; font-weight: 600; color: #cbd5e1; margin-bottom: 4px;">
                🎓 Projeto Educacional de Código Aberto (Open Source) — Licença MIT
            </p>
            <p style="font-size: 0.85rem; color: #94a3b8; margin-top: 0; margin-bottom: 16px;">
                Desenvolvido para o curso de <em>Aperfeiçoamento Profissional em Marketing Digital com Inteligência Artificial</em> — <strong>SENAI-SP</strong>.
            </p>
            <div style="background-color: rgba(245, 158, 11, 0.08); border-left: 4px solid #f59e0b; padding: 12px 18px; border-radius: 6px; text-align: left; max-width: 950px; margin: 0 auto;">
                <p style="font-size: 0.78rem; color: #fbbf24; margin: 0; line-height: 1.5;">
                    ⚠️ <strong>Aviso Legal / Disclaimer:</strong> Este software tem finalidade estritamente didática e acadêmica. As predições, cálculos de métricas de mídia, estimativas de leilão e diagnósticos gerados por estes modelos de IA são simulações para aprendizado e não substituem plataformas oficiais de anúncios (Meta Ads, Google Ads), ferramentas homologadas de CRM ou a responsabilidade técnica de profissionais habilitados.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

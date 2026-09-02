import streamlit as st
import base64

def generate_html_report(title: str, subtitle: str, sections: list) -> str:
    """
    Gera um documento HTML completo e estilizado com design moderno para o aluno abrir no navegador.
    sections: lista de tuplas (titulo_secao, conteudo_html)
    """
    sections_html = ""
    for sec_title, sec_content in sections:
        sections_html += f"""
        <div class="section-card">
            <h2>{sec_title}</h2>
            <div class="section-body">
                {sec_content}
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Relatório de Marketing com IA</title>
    <style>
        :root {{
            --primary: #e11d48;
            --primary-dark: #be123c;
            --bg: #0f172a;
            --card-bg: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border: #334155;
            --accent: #38bdf8;
        }}
        body {{
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            margin: 0;
            padding: 40px 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 850px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid var(--border);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .badge {{
            display: inline-block;
            background: var(--primary);
            color: white;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 4px 12px;
            border-radius: 20px;
            margin-bottom: 10px;
        }}
        h1 {{
            margin: 10px 0;
            color: #ffffff;
            font-size: 2rem;
        }}
        .subtitle {{
            color: var(--text-muted);
            margin: 0;
            font-size: 1.1rem;
        }}
        .section-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }}
        h2 {{
            color: var(--accent);
            border-bottom: 2px solid var(--border);
            padding-bottom: 8px;
            margin-top: 0;
            font-size: 1.3rem;
        }}
        .section-body {{
            color: #cbd5e1;
            font-size: 1rem;
        }}
        .highlight-box {{
            background: rgba(56, 189, 248, 0.1);
            border-left: 4px solid var(--accent);
            padding: 12px 16px;
            margin: 12px 0;
            border-radius: 0 8px 8px 0;
        }}
        .footer {{
            text-align: center;
            color: var(--text-muted);
            font-size: 0.85rem;
            margin-top: 40px;
            border-top: 1px solid var(--border);
            padding-top: 20px;
        }}
        pre {{
            background: #090d16;
            padding: 12px;
            border-radius: 6px;
            overflow-x: auto;
            color: #38bdf8;
        }}
        @media print {{
            body {{
                background: white;
                color: black;
            }}
            .section-card {{
                border: 1px solid #ccc;
                background: white;
                color: black;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="badge">SENAI • Marketing Digital com IA</span>
            <h1>{title}</h1>
            <p class="subtitle">{subtitle}</p>
        </div>
        
        {sections_html}

        <div class="footer">
            <p>Relatório gerado via <strong>Marketing AI Lab</strong> • Curso de Aperfeiçoamento Profissional SENAI</p>
        </div>
    </div>
</body>
</html>
"""
    return html

def render_download_button(label: str, data: str, file_name: str, mime: str = "text/html"):
    """Renderiza botão de download estilizado no Streamlit."""
    st.download_button(
        label=label,
        data=data,
        file_name=file_name,
        mime=mime,
        use_container_width=True
    )

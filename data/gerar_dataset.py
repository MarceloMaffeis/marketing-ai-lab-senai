import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

canaviais = [
    {"canal": "Meta Ads (Instagram/Facebook)", "cpm_base": 18.5, "ctr_base": 1.8, "cvr_base": 3.2, "ticket_medio": 180},
    {"canal": "Google Ads (Search)", "cpm_base": 45.0, "ctr_base": 4.5, "cvr_base": 5.8, "ticket_medio": 220},
    {"canal": "TikTok Ads", "cpm_base": 12.0, "ctr_base": 2.2, "cvr_base": 2.1, "ticket_medio": 140},
    {"canal": "Display Programático (RTB)", "cpm_base": 8.5, "ctr_base": 0.8, "cvr_base": 1.4, "ticket_medio": 190},
    {"canal": "YouTube Ads (Vídeo)", "cpm_base": 22.0, "ctr_base": 1.4, "cvr_base": 2.5, "ticket_medio": 210}
]

segmentos = ["Moda & Vestuário", "Educação & Cursos", "Tecnologia B2B", "Saúde & Bem-estar", "Alimentos & Gastronomia"]
objetivos = ["Conversão / Vendas", "Geração de Leads", "Reconhecimento de Marca", "Tráfego Qualificado"]

rows = []
start_date = datetime(2025, 1, 1)

for day in range(60):
    curr_date = start_date + timedelta(days=day)
    for c_info in canaviais:
        canal = c_info["canal"]
        segmento = np.random.choice(segmentos)
        objetivo = np.random.choice(objetivos)
        
        orcamento = float(np.random.choice([150, 250, 400, 600, 1000]))
        gasto = round(orcamento * np.random.uniform(0.92, 1.0), 2)
        
        cpm = round(c_info["cpm_base"] * np.random.uniform(0.85, 1.25), 2)
        impressoes = int((gasto / cpm) * 1000)
        
        ctr = round(c_info["ctr_base"] * np.random.uniform(0.80, 1.30), 2)
        cliques = int(impressoes * (ctr / 100))
        if cliques == 0:
            cliques = 1
            
        cpc = round(gasto / cliques, 2)
        
        cvr = round(c_info["cvr_base"] * np.random.uniform(0.75, 1.35), 2)
        conversoes = int(cliques * (cvr / 100))
        cpa = round(gasto / conversoes, 2) if conversoes > 0 else gasto
        
        receita = round(conversoes * c_info["ticket_medio"] * np.random.uniform(0.9, 1.15), 2)
        roas = round(receita / gasto, 2) if gasto > 0 else 0.0
        
        rows.append({
            "Data": curr_date.strftime("%Y-%m-%d"),
            "Canal": canal,
            "Segmento": segmento,
            "Objetivo": objetivo,
            "Gasto_R$": gasto,
            "Impressoes": impressoes,
            "Cliques": cliques,
            "CTR_%": ctr,
            "CPC_R$": cpc,
            "Conversoes": conversoes,
            "Taxa_Conversao_%": cvr,
            "CPA_R$": cpa,
            "Receita_R$": receita,
            "ROAS": roas
        })

df = pd.DataFrame(rows)
df.to_csv("C:/Users/marce/.gemini/antigravity/scratch/marketing_ai_lab/data/campanhas_exemplo.csv", index=False, encoding="utf-8-sig")
print(f"Gerado com sucesso: {len(df)} registros.")

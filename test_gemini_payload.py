import requests
import json

# Teste das diferentes estruturas de payload do Gemini
# 1. Payload simples com system instruction embutido no prompt (100% universal em qualquer endpoint v1 ou v1beta)
def test_payload_structure():
    prompt = "Olá, quem é você?"
    system_instruction = "Você é a Sofia do SENAI Sorocaba."
    
    # Formato A: System Instruction no campo oficial
    payload_a = {
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ],
        "system_instruction": {
            "parts": [{"text": system_instruction}]
        }
    }
    
    # Formato B: System Instruction embutido diretamente (Zero risco de 400 por incompatibilidade de schema)
    payload_b = {
        "contents": [
            {"role": "user", "parts": [{"text": f"INSTRUÇÕES DE PERSONA:\n{system_instruction}\n\n---\nMENSAGEM DO USUÁRIO:\n{prompt}"}]}
        ]
    }
    print("Payloads estruturados!")

test_payload_structure()

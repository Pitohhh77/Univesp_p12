import os
import requests
# CORREÇÃO: Remoção de 'from models import ...' e 'from app import *' 
# para evitar dependência circular e falha no Gunicorn.

PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
# CORREÇÃO: A chave deve vir apenas da variável de ambiente por segurança.
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

# A função get_ativos_dict() foi removida pois não é necessária e causava erro de contexto.

def gerar_relatorio_ia(prompt: str,
                      model: str = "sonar-pro",
                      max_tokens: int = 800,
                      temperature: float = 0.5) -> str:
    """
    Chama a API da Perplexity AI para gerar um relatório com base no prompt.
    Retorna o texto da resposta.
    """
    if not PERPLEXITY_API_KEY:
        # Erro claro se a chave não estiver na variável de ambiente
        raise ValueError("Chave de API da Perplexity não configurada (PERPLEXITY_API_KEY)")

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Você é um analista de investimentos financeiro simpático e didático. "
                    "Sua função é gerar um relatório de análise de carteira de ativos "
                    "com base nos dados fornecidos pelo usuário. Use linguagem amigável, "
                    "clara e objetiva. O relatório deve ter no máximo 800 tokens e ser "
                    "formatado em Markdown. Não inclua cotações de mercado reais, "
                    "apenas use os dados fornecidos. O relatório deve conter: "
                    "1. Resumo da Performance; 2. Análise de Risco e Diversificação; "
                    "3. Sugestões gerais (Compra/Venda/Manter)."
                )
            },
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    try:
        response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        error_text = getattr(e.response, 'text', '')
        raise RuntimeError(f"Erro ao chamar API Perplexity: {e} - {error_text}")
    except (KeyError, IndexError):
        raise RuntimeError(f"Resposta inesperada da API Perplexity: {response.text}")

def format_ativo(inv: dict) -> str:
    """
    Formata os dados de um ativo (dicionário) para o prompt da IA.
    """
    # Acesso seguro via .get() pois inv é um dicionário
    ticker = inv.get("ticker", "N/A")
    nome = inv.get("nome", ticker)
    quantidade = inv.get("quantidade", 0)
    valor_pago = inv.get("valor_pago", 0.0)
    cotacao_atual = inv.get("cotacao_atual", 0.0)
    lucro_prejuizo = inv.get("lucro_prejuizo", 0.0) 

    return (
        f"- Ticker: {ticker}, Nome: {nome}, Quantidade: {quantidade}, "
        f"Valor Total Pago: R${valor_pago:.2f}, Cotação Atual: R${cotacao_atual:.2f}, "
        f"Lucro/Prejuízo: R${lucro_prejuizo:.2f}"
    )

def gerar_relatorio_carteira(ativos: list, usuario: str) -> str:
    """
    Monta um prompt específico para relatório da carteira do usuário
    e chama gerar_relatorio_ia().
    """
    if not ativos:
        return (
            "## Relatório de Carteira - Vazio\n\n"
            "Não foi possível gerar a análise. Adicione seus ativos na Dashboard "
            "para que a Perplexity AI possa calcular o relatório!"
        )

    ativos_formatados = "\n".join([format_ativo(a) for a in ativos])

    prompt = (
        f"Gere um relatório de investimento para o usuário '{usuario}' baseado na seguinte carteira de ativos:\n\n"
        f"--- Ativos ---\n"
        f"{ativos_formatados}\n"
        f"--------------\n\n"
        "Com base nos dados fornecidos, realize a análise seguindo as instruções do System Role."
    )
    
    return gerar_relatorio_ia(prompt)

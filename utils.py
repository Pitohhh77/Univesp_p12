# utils.py
from gpt4all import GPT4All
import os
import threading


# Inicializa o modelo
#model = GPT4All("snip-340m-chat-v0.2.Q4_K_S.gguf")


# --- Funções que analisam os investimentos separadamente (Mantidas) ---

def analisar_risco(investimentos):
    prompt = "Analise o risco dos seguintes investimentos:\n"
    for i in investimentos:
        prompt += f"{i.nome}: Valor pago R${i.valor_pago:.2f}, Cotação atual R${i.cotacao_atual:.2f}\n"
    return model.generate(prompt)


def analisar_lucro_prejuizo(investimentos):
    prompt = "Analise o lucro ou prejuízo dos seguintes investimentos:\n"
    for i in investimentos:
        prompt += f"{i.nome}: Lucro/Prejuízo R${i.lucro_prejuizo:.2f}\n"
    return model.generate(prompt)


def analisar_diversificacao(investimentos):
    prompt = "Analise a diversificação da carteira:\n"
    for i in investimentos:
        prompt += f"{i.nome}\n"
    return model.generate(prompt)


def sugerir_compras_vendas(investimentos):
    prompt = "Sugira possíveis compras ou vendas com base nos investimentos:\n"
    for i in investimentos:
        prompt += f"{i.nome}: Cotação atual R${i.cotacao_atual:.2f}\n"
    return model.generate(prompt)


def alertas_importantes(investimentos):
    prompt = "Liste alertas importantes para esses investimentos:\n"
    for i in investimentos:
        prompt += f"{i.nome}: Lucro/Prejuízo R${i.lucro_prejuizo:.2f}\n"
    return model.generate(prompt)


def dicas_melhoria(investimentos):
    prompt = "Dê dicas de melhoria na carteira:\n"
    for i in investimentos:
        prompt += f"{i.nome}\n"
    return model.generate(prompt)


def oportunidades(investimentos):
    prompt = "Identifique oportunidades de investimento:\n"
    for i in investimentos:
        prompt += f"{i.nome}\n"
    return model.generate(prompt)


def monitoramento(investimentos):
    prompt = "Sugira estratégias de monitoramento para os investimentos:\n"
    for i in investimentos:
        prompt += f"{i.nome}\n"
    return model.generate(prompt)


def motivacao(investimentos):
    prompt = "Crie mensagens de incentivo para o investidor:\n"
    for i in investimentos:
        prompt += f"{i.nome}\n"
    return model.generate(prompt)


def resumo_geral(investimentos):
    prompt = "Faça um resumo geral dos investimentos:\n"
    for i in investimentos:
        prompt += f"{i.nome}: Valor pago R${i.valor_pago:.2f}, Cotação atual R${i.cotacao_atual:.2f}, Lucro/Prejuízo R${i.lucro_prejuizo:.2f}\n"
    return model.generate(prompt)


# --- Função principal que chama as 10 análises (Melhoria de Acessibilidade) ---
def gerar_relatorio_llm(investimentos):
    if not investimentos:
        return "<p>Nenhum investimento cadastrado. Adicione seus ativos para gerar o relatório.</p>"

    relatorio = ""
    # Alterado "1. Risco:\n" para <h2>1. Análise de Risco</h2>
    # O texto gerado (analisar_risco) agora é envolvido em uma tag <p>
    relatorio += "<h2>1. Análise de Risco</h2>" + "<p>" + analisar_risco(investimentos) + "</p>"
    relatorio += "<h2>2. Lucro e Prejuízo</h2>" + "<p>" + analisar_lucro_prejuizo(investimentos) + "</p>"
    relatorio += "<h2>3. Diversificação</h2>" + "<p>" + analisar_diversificacao(investimentos) + "</p>"
    relatorio += "<h2>4. Sugestão de Compras e Vendas</h2>" + "<p>" + sugerir_compras_vendas(investimentos) + "</p>"
    relatorio += "<h2>5. Alertas Importantes</h2>" + "<p>" + alertas_importantes(investimentos) + "</p>"
    relatorio += "<h2>6. Dicas de Melhoria na Carteira</h2>" + "<p>" + dicas_melhoria(investimentos) + "</p>"
    relatorio += "<h2>7. Oportunidades de Investimento</h2>" + "<p>" + oportunidades(investimentos) + "</p>"
    relatorio += "<h2>8. Estratégias de Monitoramento</h2>" + "<p>" + monitoramento(investimentos) + "</p>"
    relatorio += "<h2>9. Mensagens de Incentivo</h2>" + "<p>" + motivacao(investimentos) + "</p>"
    relatorio += "<h2>10. Resumo Geral</h2>" + "<p>" + resumo_geral(investimentos) + "</p>"

    return relatorio
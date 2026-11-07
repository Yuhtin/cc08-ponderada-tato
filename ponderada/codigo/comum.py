"""
comum.py: parâmetros e funções compartilhados pelas três versões da questão A4.

Aluno: Davi Duarte Rodrigues (D1 = 4, D2 = 9, N = 7).

Este módulo não sincroniza nada. Ele só guarda os parâmetros do experimento,
compara o que o sensor gerou com o que o motor recebeu e imprime o resultado.
Cada versão (versao1.py, versao2.py, versao3.py) implementa o próprio buffer.
"""

N = 7               # posições do buffer: 3 + (D2 mod 5) = 3 + (9 mod 5) = 7
TOTAL = 20_000      # amostras geradas em cada execução
EXECUCOES = 3       # execuções de cada versão
LIMITE_S = 1.0      # tempo sem receber nada que caracteriza travamento


def contar(recebidas, total=TOTAL):
    """Compara as amostras recebidas pelo consumidor com as esperadas.

    Parâmetros:
        recebidas: lista com os números das amostras, na ordem em que o
            consumidor as leu.
        total: quantidade de amostras esperadas, numeradas de 0 a total - 1.

    Retorno:
        Tupla (consumidas, perdidas, duplicadas):
        - consumidas: quantas leituras o consumidor fez;
        - perdidas: quantos números de 0 a total - 1 nunca foram lidos;
        - duplicadas: quantas leituras repetiram um número já lido.
    """
    consumidas = len(recebidas)
    distintas = len(set(recebidas))
    return consumidas, total - distintas, consumidas - distintas


def imprimir_cabecalho(titulo):
    """Imprime o título da versão e o cabeçalho da tabela de resultados.

    Parâmetros:
        titulo: nome da versão.

    Retorno:
        Nenhum. A função só escreve na saída padrão.
    """
    print(f"{titulo} | N = {N} | {TOTAL} amostras | {EXECUCOES} execuções")
    print(f"{'exec':<5}{'consumidas':>11}{'perdidas':>10}{'duplicadas':>12}"
          f"{'travou':>8}{'tempo (s)':>11}")


def imprimir_linha(execucao, recebidas, travou, segundos):
    """Imprime o resultado de uma execução como uma linha da tabela.

    Parâmetros:
        execucao: número da execução, a partir de 1.
        recebidas: lista de amostras lidas pelo consumidor.
        travou: True se o consumidor ficou LIMITE_S segundos sem receber nada.
        segundos: duração da execução, incluindo o tempo de espera do travamento.

    Retorno:
        Nenhum. A função só escreve na saída padrão.
    """
    consumidas, perdidas, duplicadas = contar(recebidas)
    print(f"{execucao:<5}{consumidas:>11}{perdidas:>10}{duplicadas:>12}"
          f"{'sim' if travou else 'não':>8}{segundos:>11.2f}")

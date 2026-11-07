"""
versao1.py: buffer circular SEM sincronização (questão A4, versão 1).

O sensor (produtor) e o motor (consumidor) dividem um contador de posições
ocupadas e usam espera ocupada. Atualizar o contador não é uma operação atômica:
cada thread lê o valor, cede a CPU com time.sleep(0) e só então escreve. Esse
sleep simula a thread sendo interrompida no pior momento e expõe a corrida.

Uso: python3 versao1.py
"""

import threading
import time

from comum import EXECUCOES, LIMITE_S, N, TOTAL, imprimir_cabecalho, imprimir_linha


class Estado:
    """Dados que as duas threads compartilham, sem nenhuma proteção."""

    def __init__(self):
        """Cria o buffer vazio e o contador zerado. Não recebe parâmetros."""
        self.buffer = [None] * N
        self.ocupadas = 0
        self.encerrar = False


def produtor(estado):
    """Gera as amostras 0 a TOTAL - 1 e as coloca no buffer.

    Parâmetros:
        estado: objeto Estado compartilhado com o consumidor.

    Retorno:
        Nenhum. A thread termina ao gerar tudo ou quando estado.encerrar vira True.
    """
    entrada = 0
    for amostra in range(TOTAL):
        while estado.ocupadas >= N:          # espera ocupada: buffer cheio
            if estado.encerrar:
                return
            time.sleep(0)
        estado.buffer[entrada] = amostra
        entrada = (entrada + 1) % N
        # Início da região crítica: leitura, troca de thread e escrita.
        lido = estado.ocupadas
        time.sleep(0)
        estado.ocupadas = lido + 1
        # Fim da região crítica.


def consumidor(estado, recebidas):
    """Retira amostras do buffer até ler TOTAL vezes ou detectar travamento.

    Parâmetros:
        estado: objeto Estado compartilhado com o produtor.
        recebidas: lista em que cada amostra lida é acrescentada.

    Retorno:
        True se ficou LIMITE_S segundos sem receber nada; False caso contrário.
    """
    saida = 0
    while len(recebidas) < TOTAL:
        inicio_espera = time.monotonic()
        while estado.ocupadas <= 0:          # espera ocupada: buffer vazio
            if time.monotonic() - inicio_espera >= LIMITE_S:
                return True
            time.sleep(0)
        recebidas.append(estado.buffer[saida])
        saida = (saida + 1) % N
        # Início da região crítica: leitura, troca de thread e escrita.
        lido = estado.ocupadas
        time.sleep(0)
        estado.ocupadas = lido - 1
        # Fim da região crítica.
    return False


def executar():
    """Roda uma execução completa da versão 1.

    Retorno:
        Tupla (recebidas, travou, segundos), no formato de comum.imprimir_linha.
    """
    estado = Estado()
    recebidas = []
    resultado = {}

    def alvo_consumidor():
        """Guarda o retorno do consumidor, que Thread não devolve sozinha."""
        resultado["travou"] = consumidor(estado, recebidas)

    t_produtor = threading.Thread(target=produtor, args=(estado,))
    t_consumidor = threading.Thread(target=alvo_consumidor)
    inicio = time.monotonic()
    t_produtor.start()
    t_consumidor.start()
    t_consumidor.join()
    estado.encerrar = True                   # libera o produtor, se estiver preso
    t_produtor.join()
    return recebidas, resultado["travou"], time.monotonic() - inicio


if __name__ == "__main__":
    imprimir_cabecalho("Versão 1: sem sincronização")
    for i in range(1, EXECUCOES + 1):
        imprimir_linha(i, *executar())

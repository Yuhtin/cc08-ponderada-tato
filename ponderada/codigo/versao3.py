"""
versao3.py: igual à versão 2, mas com a ordem do produtor trocada (questão A4, versão 3).

Três semáforos coordenam o sensor (produtor) e o motor (consumidor):
- vazio (começa em N): posições livres. Segura o produtor com o buffer cheio.
- cheio (começa em 0): posições ocupadas. Segura o consumidor com o buffer vazio.
- mutex (começa em 1): só uma thread mexe no buffer por vez.

O time.sleep(0) da versão 1 continua dentro da região crítica, para que o teste
seja igualmente hostil. Aqui ele não causa dano, porque a outra thread não entra.
O timeout existe só para detectar travamento e encerrar o experimento.

A única mudança: o produtor faz wait(mutex) antes de wait(vazio). Com o buffer
cheio, ele dorme em vazio segurando o mutex, de que o consumidor precisa para
liberar uma posição.

Uso: python3 versao3.py
"""

import threading
import time

from comum import EXECUCOES, LIMITE_S, N, TOTAL, imprimir_cabecalho, imprimir_linha


class Estado:
    """Buffer, contador e os três semáforos compartilhados pelas threads."""

    def __init__(self):
        """Cria o buffer vazio e os semáforos. Não recebe parâmetros."""
        self.buffer = [None] * N
        self.ocupadas = 0
        self.vazio = threading.Semaphore(N)
        self.cheio = threading.Semaphore(0)
        self.mutex = threading.Semaphore(1)
        self.encerrar = False


def esperar(semaforo, estado):
    """Faz wait() no semáforo, voltando periodicamente para checar o encerramento.

    Parâmetros:
        semaforo: semáforo em que a thread vai esperar.
        estado: objeto Estado, consultado para saber se o experimento acabou.

    Retorno:
        True se adquiriu o semáforo; False se o experimento foi encerrado antes.
    """
    while not estado.encerrar:
        if semaforo.acquire(timeout=0.05):
            return True
    return False


def produtor(estado):
    """Gera as amostras 0 a TOTAL - 1 na ordem TROCADA: wait(mutex), depois wait(vazio).

    Parâmetros:
        estado: objeto Estado compartilhado com o consumidor.

    Retorno:
        Nenhum. A thread termina ao gerar tudo ou quando estado.encerrar vira True.
    """
    entrada = 0
    for amostra in range(TOTAL):
        if not esperar(estado.mutex, estado):    # trocado em relação à versão 2
            return
        if not esperar(estado.vazio, estado):
            return
        estado.buffer[entrada] = amostra
        entrada = (entrada + 1) % N
        lido = estado.ocupadas
        time.sleep(0)
        estado.ocupadas = lido + 1
        estado.mutex.release()
        estado.cheio.release()


def consumidor(estado, recebidas):
    """Retira amostras na ordem wait(cheio), depois wait(mutex).

    Parâmetros:
        estado: objeto Estado compartilhado com o produtor.
        recebidas: lista em que cada amostra lida é acrescentada.

    Retorno:
        True se ficou LIMITE_S segundos sem receber nada; False caso contrário.
    """
    saida = 0
    while len(recebidas) < TOTAL:
        if not estado.cheio.acquire(timeout=LIMITE_S):
            return True
        if not estado.mutex.acquire(timeout=LIMITE_S):
            return True
        recebidas.append(estado.buffer[saida])
        saida = (saida + 1) % N
        lido = estado.ocupadas
        time.sleep(0)
        estado.ocupadas = lido - 1
        estado.mutex.release()
        estado.vazio.release()
    return False


def executar():
    """Roda uma execução completa da versão 3.

    Se houver travamento, imprime o valor dos semáforos naquele instante, antes
    de encerrar o produtor. É a evidência de quem está esperando quem.

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
    if resultado["travou"]:
        print(f"  no travamento: mutex = {estado.mutex._value}, "
              f"vazio = {estado.vazio._value}, cheio = {estado.cheio._value}, "
              f"ocupadas = {estado.ocupadas}")
    estado.encerrar = True                   # libera o produtor, se estiver preso
    t_produtor.join()
    return recebidas, resultado["travou"], time.monotonic() - inicio


if __name__ == "__main__":
    imprimir_cabecalho("Versão 3: ordem trocada no produtor")
    for i in range(1, EXECUCOES + 1):
        imprimir_linha(i, *executar())

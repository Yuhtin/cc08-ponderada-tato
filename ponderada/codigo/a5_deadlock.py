"""
a5_deadlock.py: testa o código da questão A5 e a correção de prevenção proposta.

Roda as três threads do enunciado (sensor, log e config) disputando os semáforos
i2c, log e ble, em duas montagens:
- original: thread_config segura ble enquanto pede i2c, como no enunciado;
- corrigida: thread_config solta ble antes de pedir i2c.

O time.sleep(0) entre os pedidos força a troca de thread no pior momento. Uma
thread que fica LIMITE_S segundos esperando um semáforo registra o travamento.

Uso: python3 a5_deadlock.py
"""

import threading
import time

from comum import EXECUCOES, LIMITE_S

VOLTAS = 5_000      # voltas que cada thread tenta completar em cada execução


def pedir(semaforo, estado):
    """Faz P(semaforo), registrando travamento se a espera passar do limite.

    Parâmetros:
        semaforo: semáforo pedido pela thread.
        estado: dicionário compartilhado com a chave "travou".

    Retorno:
        True se adquiriu o semáforo; False se houve travamento.
    """
    if estado["travou"]:
        return False
    if semaforo.acquire(timeout=LIMITE_S):
        return True
    estado["travou"] = True
    return False


def volta_aninhada(primeiro, segundo, estado):
    """Faz uma volta segurando os dois recursos, como as threads do enunciado.

    Parâmetros:
        primeiro: semáforo pedido antes, e mantido durante o segundo pedido.
        segundo: semáforo pedido com o primeiro ainda em posse.
        estado: dicionário compartilhado com a chave "travou".

    Retorno:
        True se completou a volta; False se houve travamento.
    """
    if not pedir(primeiro, estado):
        return False
    time.sleep(0)
    if not pedir(segundo, estado):
        return False
    time.sleep(0)
    segundo.release()
    primeiro.release()
    return True


def volta_separada(primeiro, segundo, estado):
    """Faz uma volta usando um recurso de cada vez, como na correção.

    Parâmetros:
        primeiro: semáforo usado e liberado antes de pedir o segundo.
        segundo: semáforo usado depois.
        estado: dicionário compartilhado com a chave "travou".

    Retorno:
        True se completou a volta; False se houve travamento.
    """
    if not pedir(primeiro, estado):
        return False
    time.sleep(0)
    primeiro.release()
    if not pedir(segundo, estado):
        return False
    time.sleep(0)
    segundo.release()
    return True


def executar(corrigida):
    """Roda uma execução com as três threads.

    Parâmetros:
        corrigida: True para a montagem corrigida; False para a original.

    Retorno:
        Tupla (voltas, travou), com a lista de voltas completas de cada thread,
        na ordem sensor, log, config, e se houve travamento.
    """
    i2c, log, ble = (threading.Semaphore(1) for _ in range(3))
    estado = {"travou": False}
    voltas = [0, 0, 0]
    volta_config = volta_separada if corrigida else volta_aninhada
    planos = [(volta_aninhada, i2c, log), (volta_aninhada, log, ble), (volta_config, ble, i2c)]

    def rodar(indice):
        """Repete a volta da thread até completar VOLTAS ou travar."""
        volta, primeiro, segundo = planos[indice]
        while voltas[indice] < VOLTAS and volta(primeiro, segundo, estado):
            voltas[indice] += 1

    threads = [threading.Thread(target=rodar, args=(i,)) for i in range(3)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return voltas, estado["travou"]


if __name__ == "__main__":
    print(f"A5: {VOLTAS} voltas por thread | {EXECUCOES} execuções")
    print(f"{'montagem':<11}{'exec':<6}{'sensor':>8}{'log':>8}{'config':>8}{'travou':>8}")
    for nome, corrigida in (("original", False), ("corrigida", True)):
        for i in range(1, EXECUCOES + 1):
            voltas, travou = executar(corrigida)
            print(f"{nome:<11}{i:<6}{voltas[0]:>8}{voltas[1]:>8}{voltas[2]:>8}"
                  f"{'sim' if travou else 'não':>8}")

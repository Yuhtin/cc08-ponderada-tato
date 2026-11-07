# Ponderada CC08: do pipeline ao deadlock

**Aluno:** Davi Duarte Rodrigues

Análise técnica e decisão de CTO sobre a pulseira sensorial Tato, com o código das questões A4 e A5.

O documento da entrega é [`ponderada/ponderada-tato.md`](ponderada/ponderada-tato.md).

Atividade bônus no Colab: [pipelines e paralelismo](https://colab.research.google.com/drive/1Q0tV1KXpDZUSuS1X0oPXCfUGBVscTtT0).

## Como rodar a questão A4

É preciso ter Python 3, sem instalar nenhuma dependência. Primeiro, entre na pasta do código:

```bash
cd ponderada/codigo
```

Cada comando abaixo roda uma versão, com 3 execuções de 20.000 amostras e N = 7:

```bash
python3 versao1.py   # sem sincronização: perde e duplica amostras
python3 versao2.py   # com semáforos: funciona
python3 versao3.py   # ordem trocada no produtor: deadlock
```

A versão 3 detecta o travamento depois de 1 s sem receber amostras, registra o resultado e encerra sozinha.

## Teste da correção da questão A5

Na mesma pasta, este comando roda o código do enunciado e a correção proposta:

```bash
python3 a5_deadlock.py
```

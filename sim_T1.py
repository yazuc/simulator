import heapq
import yaml
import random

# ===== Funções de apoio =====

def uniforme(a, b, x):
    return a + (b - a) * x

def gerador_mcl(X0, a, c, M, n):
    numeros = []
    Xn = X0
    for _ in range(n):
        Xn = (a * Xn + c) % M
        numeros.append(Xn / M)
    return numeros

def escolhe_destino(roteamento, sorteio):
    acumulado = 0
    for destino, probabilidade in roteamento.items():
        acumulado += probabilidade
        if sorteio <= acumulado:
            return destino
    return "saida"  # fallback

# ===== Classes =====

class Evento:
    def __init__(self, tipo, tempo, fila_origem=None, fila_destino=None):
        self.tipo = tipo
        self.tempo = tempo
        self.fila_origem = fila_origem
        self.fila_destino = fila_destino

    def __lt__(self, outro):
        return self.tempo < outro.tempo

class Fila:
    def __init__(self, id, servidores, capacidade, atendimento_min, atendimento_max, roteamento):
        self.id = id
        self.servidores = servidores
        self.capacidade = capacidade
        self.atendimento_min = atendimento_min
        self.atendimento_max = atendimento_max
        self.roteamento = roteamento
        self.fila = 0
        self.servidores_ocupados = 0
        self.tempo_fila = {i: 0 for i in range(capacidade + 1)}
        self.ultimo_tempo = 0
        self.clientes_perdidos = 0
        self.total_chegadas = 0  
        self.total_atendidos = 0  

# ===== Carrega Modelo =====

with open("modelo.yml", "r") as f:
    modelo = yaml.safe_load(f)

filas = {}
for id_fila, dados in modelo["filas"].items():
    filas[int(id_fila)] = Fila(
        id=int(id_fila),
        servidores=dados["servidores"],
        capacidade=dados["capacidade"],
        atendimento_min=dados["atendimento_min"],
        atendimento_max=dados["atendimento_max"],
        roteamento=dados.get("roteamento", {})
    )

# ===== Parâmetros =====

chegada_info = modelo["chegada"]
fila_chegada = filas[chegada_info["fila"]]
chegada_min = chegada_info["intervalo_min"]
chegada_max = chegada_info["intervalo_max"]
tempo_primeira_chegada = chegada_info["tempo_primeira"]

total_aleatorios = 100000
numeros_aleatorios = gerador_mcl(X0=55, a=423232, c=8743123, M=3232312318, n=total_aleatorios)
indice_aleatorio = 0

eventos = []
heapq.heappush(eventos, Evento("CHEGADA", tempo_primeira_chegada, fila_destino=fila_chegada))

tempo_final = 0

# ===== Loop Principal =====

while eventos and indice_aleatorio < total_aleatorios:
    evento = heapq.heappop(eventos)
    tempo_atual = evento.tempo

    for fila in filas.values():
        fila.tempo_fila[fila.fila] += tempo_atual - fila.ultimo_tempo
        fila.ultimo_tempo = tempo_atual

    if evento.tipo == "CHEGADA":
        fila = evento.fila_destino
        fila.total_chegadas += 1  
        if fila.fila < fila.capacidade:
            fila.fila += 1
            fila.total_atendidos += 1
            if fila.servidores_ocupados < fila.servidores:
                fila.servidores_ocupados += 1
                fila.fila -= 1
                if indice_aleatorio < total_aleatorios:
                    sorteio = numeros_aleatorios[indice_aleatorio]
                    indice_aleatorio += 1
                    tempo_servico = uniforme(fila.atendimento_min, fila.atendimento_max, sorteio)
                    heapq.heappush(eventos, Evento("SAIDA", tempo_atual + tempo_servico, fila_origem=fila))
        else:
            fila.clientes_perdidos += 1

        if fila == fila_chegada and indice_aleatorio < total_aleatorios:
            sorteio = numeros_aleatorios[indice_aleatorio]
            indice_aleatorio += 1
            tempo_chegada = uniforme(chegada_min, chegada_max, sorteio)
            heapq.heappush(eventos, Evento("CHEGADA", tempo_atual + tempo_chegada, fila_destino=fila_chegada))

    elif evento.tipo == "SAIDA":
        fila = evento.fila_origem
        fila.servidores_ocupados -= 1

        if fila.roteamento and indice_aleatorio < total_aleatorios:
            sorteio = numeros_aleatorios[indice_aleatorio]
            indice_aleatorio += 1
            destino = escolhe_destino(fila.roteamento, sorteio)
            if destino != "saida":
                destino_fila = filas[int(destino)]
                heapq.heappush(eventos, Evento("PASSAGEM", tempo_atual, fila_origem=fila, fila_destino=destino_fila))

        if fila.fila > 0 and fila.servidores_ocupados < fila.servidores and indice_aleatorio < total_aleatorios:
            fila.fila -= 1
            fila.servidores_ocupados += 1
            sorteio = numeros_aleatorios[indice_aleatorio]
            indice_aleatorio += 1
            tempo_servico = uniforme(fila.atendimento_min, fila.atendimento_max, sorteio)
            heapq.heappush(eventos, Evento("SAIDA", tempo_atual + tempo_servico, fila_origem=fila))

    elif evento.tipo == "PASSAGEM":
        fila = evento.fila_destino
        fila.total_chegadas += 1
        if fila.fila < fila.capacidade:
            fila.fila += 1
            if fila.servidores_ocupados < fila.servidores:
                fila.servidores_ocupados += 1
                fila.total_atendidos += 1
                fila.fila -= 1
                if indice_aleatorio < total_aleatorios:
                    sorteio = numeros_aleatorios[indice_aleatorio]
                    indice_aleatorio += 1
                    tempo_servico = uniforme(fila.atendimento_min, fila.atendimento_max, sorteio)
                    heapq.heappush(eventos, Evento("SAIDA", tempo_atual + tempo_servico, fila_origem=fila))
        else:
            fila.clientes_perdidos += 1

    tempo_final = tempo_atual

# Atualiza tempos finais
for fila in filas.values():
    fila.tempo_fila[fila.fila] += tempo_final - fila.ultimo_tempo

# ===== Relatórios =====

def relatorio(fila):
    tempo_total = sum(fila.tempo_fila.values())
    populacao_media = sum(tempo * n for n, tempo in fila.tempo_fila.items()) / tempo_total
    taxa_atendimento = (fila.total_atendidos / fila.total_chegadas) * 100 if fila.total_chegadas > 0 else 0
    taxa_rejeicao = (fila.clientes_perdidos / fila.total_chegadas) * 100 if fila.total_chegadas > 0 else 0

    print(f"\n--- Fila {fila.id} ---")
    print(f"Clientes perdidos: {fila.clientes_perdidos}")
    print(f"Total de chegadas: {fila.total_chegadas}")
    print(f"Total de atendidos: {fila.total_atendidos}")
    print(f"Taxa de atendimento: {taxa_atendimento:.2f}%")
    print(f"Taxa de rejeição: {taxa_rejeicao:.2f}%")
    print(f"População média: {populacao_media:.2f}")
    print("Tempo total em cada estado da fila:")
    for i in range(fila.capacidade + 1):
        print(f"  Fila {i}: {fila.tempo_fila[i]:.2f} minutos")


print(f"\nSimulação encerrada após {tempo_final:.2f} minutos.")
for fila in filas.values():
    relatorio(fila)

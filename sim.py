import heapq

def uniforme(a, b, x):
    return a + (b - a) * x

def gerador_mcl(X0, a, c, M, n):
    numeros = []
    Xn = X0
    for _ in range(n):
        Xn = (a * Xn + c) % M
        numeros.append(Xn / M)
    return numeros

class Evento:
    def __init__(self, tipo, tempo, fila_origem=None, fila_destino=None):
        self.tipo = tipo  # "CHEGADA", "SAIDA", "PASSAGEM"
        self.tempo = tempo
        self.fila_origem = fila_origem
        self.fila_destino = fila_destino

    def __lt__(self, outro):
        return self.tempo < outro.tempo

class Fila:
    def __init__(self, id, servidores, capacidade, atendimento_min, atendimento_max):
        self.id = id
        self.servidores = servidores
        self.capacidade = capacidade
        self.atendimento_min = atendimento_min
        self.atendimento_max = atendimento_max
        self.fila = 0
        self.servidores_ocupados = 0
        self.tempo_fila = {i: 0 for i in range(capacidade + 1)}
        self.ultimo_tempo = 0
        self.clientes_perdidos = 0

# Parâmetros
total_aleatorios = 100000
X0 = 55
a = 423232
c = 8743123
M = 3232312318
numeros_aleatorios = gerador_mcl(X0, a, c, M, total_aleatorios)
indice_aleatorio = 0

# Fila 1: G/G/2/3, chegada entre [1..4], serviço entre [3..4]
# Fila 2: G/G/1/5, serviço entre [2..3]
fila1 = Fila(1, servidores=2, capacidade=3, atendimento_min=3.0, atendimento_max=4.0)
fila2 = Fila(2, servidores=1, capacidade=5, atendimento_min=2.0, atendimento_max=3.0)

chegada_min, chegada_max = 1.0, 4.0
tempo_primeira_chegada = 1.5

eventos = []
heapq.heappush(eventos, Evento("CHEGADA", tempo_primeira_chegada, fila_destino=fila1))

tempo_final = 0

while eventos and indice_aleatorio < total_aleatorios:
    evento = heapq.heappop(eventos)
    tempo_atual = evento.tempo

    # Atualiza tempos de estado
    for fila in [fila1, fila2]:
        fila.tempo_fila[fila.fila] += tempo_atual - fila.ultimo_tempo
        fila.ultimo_tempo = tempo_atual

    if evento.tipo == "CHEGADA":
        fila = evento.fila_destino
        if fila.fila < fila.capacidade:
            fila.fila += 1
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

        # Próxima chegada externa só vai para a Fila 1
        if fila == fila1 and indice_aleatorio < total_aleatorios:
            sorteio = numeros_aleatorios[indice_aleatorio]
            indice_aleatorio += 1
            tempo_chegada = uniforme(chegada_min, chegada_max, sorteio)
            heapq.heappush(eventos, Evento("CHEGADA", tempo_atual + tempo_chegada, fila_destino=fila1))

    elif evento.tipo == "SAIDA":
        fila = evento.fila_origem
        fila.servidores_ocupados -= 1

        # Se for a Fila 1, agenda passagem para a Fila 2
        if fila == fila1:
            heapq.heappush(eventos, Evento("PASSAGEM", tempo_atual, fila_origem=fila1, fila_destino=fila2))

        # Verifica se há clientes esperando na fila
        if fila.fila > 0 and fila.servidores_ocupados < fila.servidores and indice_aleatorio < total_aleatorios:
            fila.fila -= 1
            fila.servidores_ocupados += 1
            sorteio = numeros_aleatorios[indice_aleatorio]
            indice_aleatorio += 1
            tempo_servico = uniforme(fila.atendimento_min, fila.atendimento_max, sorteio)
            heapq.heappush(eventos, Evento("SAIDA", tempo_atual + tempo_servico, fila_origem=fila))

    elif evento.tipo == "PASSAGEM":
        fila = evento.fila_destino
        if fila.fila < fila.capacidade:
            fila.fila += 1
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

    tempo_final = tempo_atual

# Atualiza tempos finais
for fila in [fila1, fila2]:
    fila.tempo_fila[fila.fila] += tempo_final - fila.ultimo_tempo

# Relatórios
def relatorio(fila):
    tempo_total = sum(fila.tempo_fila.values())
    populacao_media = sum(tempo * n for n, tempo in fila.tempo_fila.items()) / tempo_total
    print(f"\n--- Fila {fila.id} ---")
    print(f"Clientes perdidos: {fila.clientes_perdidos}")
    print(f"População média: {populacao_media:.2f}")
    print("Tempo total em cada estado da fila:")
    for i in range(fila.capacidade + 1):
        print(f"  Fila {i}: {fila.tempo_fila[i]:.2f} minutos")

print(f"\nSimulação encerrada após {tempo_final:.2f} minutos.")
relatorio(fila1)
relatorio(fila2)

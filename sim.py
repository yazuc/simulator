import heapq

def uniforme(a, b, x):
    return a + (b - a) * x

def gerador_mcl(X0, a, c, M, n):
    numeros = []
    Xn = X0
    for _ in range(n):
        Xn = (a * Xn + c) % M
        numeros.append(Xn / M)  # Normaliza entre [0, 1]
    return numeros

class Evento:
    def __init__(self, tipo, tempo):
        self.tipo = tipo  # 'CHEGADA' ou 'SAIDA'
        self.tempo = tempo

    def __lt__(self, outro):
        return self.tempo < outro.tempo

# Parâmetros
total_aleatorios = 100000
chegada_min, chegada_max = 2.0, 5.0
servico_min, servico_max = 3.0, 5.0
capacidade_fila = 5
num_servidores = 1  

# Parâmetros do gerador MCL
X0 = 55
a = 423232
c = 8743123
M = 3232312318

# Lista de números pseudoaleatórios
numeros_aleatorios = gerador_mcl(X0, a, c, M, total_aleatorios)

# Inicialização da fila de eventos
eventos = []
heapq.heappush(eventos, Evento("CHEGADA", 2.0))

# Estado do sistema
fila = 0
servidores_ocupados = 0
indice_aleatorio = 0
clientes_perdidos = 0

tempo_fila = {i: 0 for i in range(capacidade_fila + 1)}
ultimo_tempo = 0
tempo_final = 0

while eventos and indice_aleatorio < total_aleatorios:
    evento = heapq.heappop(eventos)
    tempo_atual = evento.tempo
    tempo_fila[fila] += tempo_atual - ultimo_tempo
    ultimo_tempo = tempo_atual

    if evento.tipo == "CHEGADA":
        if fila < capacidade_fila:
            fila += 1
            if servidores_ocupados < num_servidores:
                servidores_ocupados += 1
                fila -= 1
                sorteio = numeros_aleatorios[indice_aleatorio]
                tempo_servico = uniforme(servico_min, servico_max, sorteio)
                indice_aleatorio += 1
                heapq.heappush(eventos, Evento("SAIDA", tempo_atual + tempo_servico))
        else:
            clientes_perdidos += 1

        if indice_aleatorio < total_aleatorios:
            sorteio = numeros_aleatorios[indice_aleatorio]
            tempo_chegada = uniforme(chegada_min, chegada_max, sorteio)
            indice_aleatorio += 1
            heapq.heappush(eventos, Evento("CHEGADA", tempo_atual + tempo_chegada))
    
    elif evento.tipo == "SAIDA":
        servidores_ocupados -= 1
        if fila > 0 and servidores_ocupados < num_servidores and indice_aleatorio < total_aleatorios:
            fila -= 1
            servidores_ocupados += 1
            sorteio = numeros_aleatorios[indice_aleatorio]
            tempo_servico = uniforme(servico_min, servico_max, sorteio)
            indice_aleatorio += 1
            heapq.heappush(eventos, Evento("SAIDA", tempo_atual + tempo_servico))

    tempo_final = tempo_atual

tempo_fila[fila] += tempo_final - ultimo_tempo

# Cálculo da população média da fila
tempo_total_simulacao = sum(tempo_fila.values())
populacao_media = sum(tempo * num_itens for num_itens, tempo in tempo_fila.items()) / tempo_total_simulacao

print(f"Simulação encerrada após {tempo_final:.2f} minutos.")
print(f"Clientes perdidos: {clientes_perdidos}")
print(f"População média da fila: {populacao_media:.2f}")
print("Tempo total em cada estado da fila:")
for i in range(capacidade_fila + 1):
    print(f"Fila {i}: {tempo_fila[i]:.1f} minutos")

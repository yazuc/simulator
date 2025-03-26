import matplotlib.pyplot as plt
import numpy as np

# Parâmetros do Método Congruente Linear
X0 = 55               # Semente
a = 423232       # Multiplicador
c = 8743123       # Incremento
M = 3232312318          # Modulo

# Função para gerar números pseudoaleatórios com MCL
def gerador_mcl(X0, a, c, M, n):
    numeros = []
    Xn = X0
    for _ in range(n):
        Xn = (a * Xn + c) % M
        numeros.append(Xn / M)  # Normaliza entre [0, 1]
    return numeros

# Gerando 1000 números pseudoaleatórios
n = 1000
numeros_aleatorios = gerador_mcl(X0, a, c, M, n)

# Salvando os números em um arquivo
with open("numeros_aleatorios.txt", "w") as f:
    for num in numeros_aleatorios:
        f.write(f"{num}\n")

plt.savefig("grafico_dispersion.png")


# Criando o gráfico de dispersão (pares consecutivos)
x = numeros_aleatorios[:-1]
y = numeros_aleatorios[1:]

plt.figure(figsize=(8, 8))
plt.scatter(x, y, s=5, c='blue', alpha=0.7)
plt.title("Gráfico de Dispersão - Método Congruente Linear")
plt.xlabel("X[n]")
plt.ylabel("X[n+1]")
plt.grid(True)
plt.savefig("grafico_dispersion.png")
plt.close()


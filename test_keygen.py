# test_keygen.py PRUEBA DE que mida el tiempo de generación de llaves y lo presente en una tablita PARTE B
#INSTALAR pip install tabulate Y CORRERlo
# test_keygen.py

import time
from KeyGenerator import generate_key_table
from SeedAndPrimes import generate_seed, generate_prime, generate_node_id
from dataclasses import dataclass
from tabulate import tabulate

@dataclass
class DummyShared:
    id: int
    P: int
    Q: int
    S: int
    N: int

NUM_PRUEBAS = 10
NUM_KEYS = 64
resultados = []

for i in range(1, NUM_PRUEBAS + 1):
    node_id = generate_node_id()
    P = generate_prime()
    Q = generate_prime()
    S = generate_seed()
    shared = DummyShared(id=node_id, P=P, Q=Q, S=S, N=NUM_KEYS)

    inicio = time.perf_counter()
    llaves = generate_key_table(shared, n_keys=NUM_KEYS)
    fin = time.perf_counter()

    tiempo = fin - inicio
    resultados.append([i, len(llaves), f"{tiempo:.8f} s"])  # más decimales

# Estadísticas
tiempos = [float(r[2].split()[0]) for r in resultados]
promedio = sum(tiempos) / len(tiempos)
minimo = min(tiempos)
maximo = max(tiempos)

tabla_detalle = tabulate(resultados, headers=["Prueba", "Número de llaves", "Tiempo de generación"], tablefmt="fancy_grid")
tabla_estadistica = tabulate([["Promedio", f"{promedio:.8f} s"],
                              ["Mínimo", f"{minimo:.8f} s"],
                              ["Máximo", f"{maximo:.8f} s"]],
                             headers=["Estadística", "Tiempo"], tablefmt="fancy_grid")

print("=== Resultados de cada prueba ===")
print(tabla_detalle)
print("\n=== Estadísticas de tiempo de generación ===")
print(tabla_estadistica)

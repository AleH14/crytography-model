"""
KeyGenerator.py
----------------
Este módulo implementa la generación de llaves de 64 bits para el modelo de 
cifrado polimórfico basado en OTP, según el paper 
"Cryptography model to secure IoT device endpoints, based on polymorphic cipher OTP".

El archivo se encarga únicamente de:
 - Definir funciones auxiliares de 64 bits.
 - Implementar las funciones fs, fg y fm descritas en el modelo.
 - Construir tablas de llaves a partir de parámetros compartidos (P, Q, S, N).

NO incluye:
 - Funciones polimórficas reversibles (van en ReversibleFunctions.py).
 - Manejo del PSN (va en PSN.py).
 - Tipos de mensajes (van en MessageTypes.py).
 - Lógica de cliente/servidor.

Autor: [Tu nombre o grupo]
Fecha: 2025
"""

import hashlib
import hmac

# ============================================================
# Constantes globales
# ============================================================

# Tamaño de las llaves en bits
KEY_BITS = 64

# Máscara para forzar valores a 64 bits
KEY_MASK = (1 << KEY_BITS) - 1


# ============================================================
# Funciones auxiliares (bitwise)
# ============================================================

def _u64(x: int) -> int:
    """
    Fuerza que un número se mantenga en 64 bits.
    """
    return x & KEY_MASK


def _rol(x: int, n: int) -> int:
    """
    Rotación a la izquierda sobre 64 bits.
    """
    n %= KEY_BITS
    return _u64((x << n) | (x >> (KEY_BITS - n)))


def _ror(x: int, n: int) -> int:
    """
    Rotación a la derecha sobre 64 bits.
    """
    n %= KEY_BITS
    return _u64((x >> n) | (x << (KEY_BITS - n)))


# ============================================================
# Funciones principales del modelo (fs, fg, fm)
# ============================================================

def fs_scrambled(p: int, s: int) -> int:
    """
    fs(x,y): Mezcla un primo P con una semilla S para generar un "embrión" P0.

    - Se usa HMAC-SHA256 con P como clave y S como mensaje.
    - El resultado se reduce a 64 bits.

    Parámetros:
        p (int): primo generado por un nodo.
        s (int): semilla compartida.

    Retorna:
        int: valor P0 de 64 bits.
    """
    key = p.to_bytes((p.bit_length() + 7) // 8 or 1, "big")
    msg = s.to_bytes((s.bit_length() + 7) // 8 or 1, "big")
    h = hmac.new(key, msg, hashlib.sha256).digest()
    return int.from_bytes(h[:8], "big") & KEY_MASK


def fg_generation(p0: int, q: int, counter: int) -> int:
    """
    fg(x,y): Genera una llave a partir de P0 y Q.

    - Se combina P0, Q y un contador en bytes.
    - Se aplica SHA-256 y se toman los 64 bits más significativos.

    Parámetros:
        p0 (int): embrión generado por fs().
        q (int): primo generado por el otro nodo.
        counter (int): número de iteración.

    Retorna:
        int: llave de 64 bits.
    """
    data = (
        p0.to_bytes(8, "big")
        + q.to_bytes(8, "big")
        + counter.to_bytes(4, "big")
    )
    h = hashlib.sha256(data).digest()
    return int.from_bytes(h[:8], "big") & KEY_MASK


def fm_mutation(s: int, q: int, counter: int) -> int:
    """
    fm(x,y): Muta la semilla S para la siguiente iteración.

    - Mezcla S con Q y el contador.
    - Aplica rotaciones y hashing para aumentar la entropía.

    Parámetros:
        s (int): semilla actual.
        q (int): primo del otro nodo.
        counter (int): número de iteración.

    Retorna:
        int: nueva semilla mutada de 64 bits.
    """
    x = _u64(s ^ (q + counter))
    x = _rol(x, (counter & 63) or 1)
    data = (
        x.to_bytes(8, "big")
        + q.to_bytes(8, "big")
        + counter.to_bytes(4, "big")
    )
    h = hashlib.sha256(data).digest()
    return int.from_bytes(h[:8], "big") & KEY_MASK


# ============================================================
# Generación de tabla de llaves
# ============================================================

def generate_key_table(shared_params, n_keys: int = None):
    """
    Genera una tabla de llaves de 64 bits a partir de parámetros compartidos.

    Flujo:
        1) fs(P, S) -> P0
        2) fg(P0, Q, counter) -> llave
        3) fm(S, Q, counter) -> nueva semilla
        4) Repetir hasta completar N llaves

    Parámetros:
        shared_params: objeto con atributos P, Q, S y N.
        n_keys (int): número de llaves a generar. 
                      Si None, usa shared_params.N.

    Retorna:
        list[int]: lista de llaves generadas.
    """
    if n_keys is None:
        n_keys = getattr(shared_params, "N", 16)  # Cambiado a 16 por defecto

    P = int(shared_params.P)
    Q = int(shared_params.Q)
    S = int(shared_params.S)

    keys = []
    seed = S
    counter = 0

    while len(keys) < n_keys:
        # 1) Embrión
        P0 = fs_scrambled(P, seed)
        # 2) Generar llave
        k = fg_generation(P0, Q, counter)
        keys.append(k & KEY_MASK)
        # 3) Mutar semilla
        seed = fm_mutation(seed, Q, counter)
        counter += 1

    return keys


# ============================================================
# Prueba rápida (ejecución directa)
# ============================================================

if __name__ == "__main__":
    from dataclasses import dataclass
    from SeedAndPrimes import generate_seed, generate_prime, generate_node_id

    @dataclass
    class DummyShared:
        id: int
        P: int
        Q: int
        S: int
        N: int

    # Generar parámetros iniciales
    node_id = generate_node_id()
    P = generate_prime()
    Q = generate_prime()
    S = generate_seed()

    shared = DummyShared(id=node_id, P=P, Q=Q, S=S, N=4)

    # Generar llaves
    keys = generate_key_table(shared, n_keys=4)
    print("=== Tabla de llaves generada ===")
    for i, k in enumerate(keys):
        print(f"K{i} = {k:016X}")

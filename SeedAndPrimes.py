from __future__ import annotations

import hashlib
import os
import platform
import secrets
import struct
import time
import uuid
from dataclasses import dataclass
from typing import Iterable, Tuple

# ---------------------------- Parámetros fijos ----------------------------
DEFAULT_KEY_BITS = 64    # Tamaño de la semilla S en bits
DEFAULT_PRIME_BITS = 64  # Tamaño de los primos P y Q en bits
DEFAULT_ID_BITS = 32     # Tamaño del identificador del nodo en bits
DEFAULT_N_KEYS = 4       # Número de llaves a generar

# ---------------------------- Recolección de entropía ----------------------------

def _collect_entropy(tag: str = "") -> bytes:
    """
    Recopila varias fuentes de entropía del sistema para generar números impredecibles.
    Se mezclan bytes aleatorios del SO, tiempos de ejecución, PID, MAC y huella del sistema.
    El parámetro `tag` permite diferenciar (cliente o servidor).
    """
    pieces = []
    # Bytes aleatorios cripto-seguros
    pieces.append(secrets.token_bytes(32))
    # Tiempos, MAC y PID empacados en binario
    pieces.append(struct.pack(
        ">QQQI",
        time.time_ns() & ((1 << 64) - 1),
        time.perf_counter_ns() & ((1 << 64) - 1),
        uuid.getnode() & ((1 << 64) - 1),
        os.getpid() & ((1 << 32) - 1),
    ))
    # Información del sistema operativo y hardware
    uname = platform.uname()
    pieces.append(f"{uname.system}|{uname.node}|{uname.release}|{uname.version}|{uname.machine}".encode())
    # Etiqueta opcional
    if tag:
        pieces.append(tag.encode())
    return b"|".join(pieces)


def _int_from_entropy(bits: int, *, tag: str = "") -> int:
    """
    Deriva un entero con los bits indicados a partir de entropía.
    Se usa SHA-256 repetidamente hasta completar el tamaño en bits requerido.
    """
    if bits < 8:
        raise ValueError("bits debe ser >= 8")
    ent = _collect_entropy(tag)
    out = 0
    need = bits
    counter = 0
    while need > 0:
        # Hash de la entropía + contador
        h = hashlib.sha256(ent + counter.to_bytes(4, "big")).digest()
        take = min(need, 256)  # Máximo 256 bits por iteración (tamaño de SHA-256)
        # Toma los bits más significativos del hash
        chunk = int.from_bytes(h, "big") >> (256 - take)
        out = (out << take) | chunk
        need -= take
        counter += 1
    # Fuerza bit más alto en 1 para asegurar la longitud correcta
    out |= 1 << (bits - 1)
    out &= (1 << bits) - 1
    # Evita número cero
    if out == 0:
        out = 1
    return out

# ---------------------------- Primalidad (Miller-Rabin) ----------------------------

def _miller_rabin(n: int, bases: Iterable[int]) -> bool:
    """
    Test probabilístico de primalidad (Miller-Rabin).
    Determina si n es primo probable usando las bases dadas.
    """
    # Pequeño filtro con primos chicos
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    if n < 2:
        return False
    for p in small_primes:
        if n % p == 0:
            return n == p
    # Descomposición de n-1 = d * 2^s
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    # Prueba con cada base
    for a in bases:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def is_probable_prime(n: int, *, rounds: int = 8) -> bool:
    """
    Verifica si un número es un primo probable usando Miller-Rabin.
    Usa algunas bases fijas y varias aleatorias (según 'rounds').
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    # Bases deterministas pequeñas
    bases = [2, 3, 5, 7, 11, 13, 17][:max(0, 7 - rounds)]
    # Añadir bases aleatorias
    for _ in range(rounds):
        a = 0
        while a < 2 or a > n - 2:
            a = 2 + secrets.randbelow(max(2, n - 3))
        bases.append(a)
    return _miller_rabin(n, bases)


def next_probable_prime(n: int) -> int:
    """
    Encuentra el siguiente número primo probable mayor o igual a n.
    Avanza de 2 en 2 (solo prueba impares).
    """
    if n <= 2:
        return 2
    n |= 1  # asegurar impar
    while not is_probable_prime(n):
        n += 2
    return n

# ---------------------------- Generadores públicos ----------------------------

def generate_node_id(bits: int = DEFAULT_ID_BITS, *, tag: str = "") -> int:
    """Genera un ID de nodo único con 32 bits."""
    return _int_from_entropy(bits, tag=f"node_id|{tag}")


def generate_seed(bits: int = DEFAULT_KEY_BITS, *, tag: str = "") -> int:
    """Genera la semilla S de 64 bits."""
    return _int_from_entropy(bits, tag=f"seed|{tag}")


def generate_prime(bits: int = DEFAULT_PRIME_BITS, *, tag: str = "") -> int:
    """
    Genera un primo probable de 64 bits.
    Si se pasa del tamaño deseado, busca un primo dentro del rango permitido.
    """
    if bits < 8:
        raise ValueError("bits de primo debe ser >= 8")
    # Número aleatorio de 'bits' bits, asegurado impar
    start = _int_from_entropy(bits, tag=f"prime|{tag}") | 1
    p = next_probable_prime(start)
    # Ajuste si se excede el número de bits
    if p.bit_length() > bits:
        candidate = (1 << bits) - 1
        candidate |= 1
        while candidate > 2 and not is_probable_prime(candidate):
            candidate -= 2
        p = candidate
    return p
def generate_psn(bits: int = 32, *, tag: str = "") -> int:
    """
    Genera un número de secuencia (PSN) de 32 bits.
    Ideal para trazabilidad de mensajes en sistemas distribuidos.
    """
    return _int_from_entropy(bits, tag=f"psn|{tag}")

# ---------------------------- Estructura compartida ----------------------------

@dataclass(frozen=True)
class SharedParams:
    id: int  # identificador del nodo
    P: int   # primo generado por cliente
    Q: int   # primo generado por servidor
    S: int   # semilla
    N: int   # número de llaves
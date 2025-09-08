# ReversibleFunctions.py
from typing import Callable

# Helpers
def xor_bytes(data: bytes, b: int) -> bytes:
    return bytes([x ^ b for x in data])

def rol_byte(b, n):
    return ((b << n) & 0xFF) | (b >> (8 - n))

def ror_byte(b, n):
    return ((b >> n) | ((b << (8 - n)) & 0xFF)) & 0xFF

# F1..F8 (y sus inversas)
def F1(data: bytes) -> bytes:
    # XOR con 0x55 (autoinverso)
    return xor_bytes(data, 0x55)

def inv_F1(data: bytes) -> bytes:
    return xor_bytes(data, 0x55)

def F2(data: bytes) -> bytes:
    # rotar cada byte a la izquierda 1 (inversa: ror 1)
    return bytes(rol_byte(b,1) for b in data)

def inv_F2(data: bytes) -> bytes:
    return bytes(ror_byte(b,1) for b in data)

def F3(data: bytes) -> bytes:
    # sumar 1 modulo 256
    return bytes((b + 1) & 0xFF for b in data)

def inv_F3(data: bytes) -> bytes:
    return bytes((b - 1) & 0xFF for b in data)

def F4(data: bytes) -> bytes:
    # restar 1 modulo 256
    return bytes((b - 1) & 0xFF for b in data)

def inv_F4(data: bytes) -> bytes:
    return bytes((b + 1) & 0xFF for b in data)

def F5(data: bytes) -> bytes:
    # invertir orden de bytes (autoinverso)
    return data[::-1]

def inv_F5(data: bytes) -> bytes:
    return data[::-1]

def F6(data: bytes) -> bytes:
    # intercambiar nibbles en cada byte: (hi<<4)|(lo>>4), autoinverso
    return bytes(((b << 4) & 0xF0) | ((b >> 4) & 0x0F) for b in data)

def inv_F6(data: bytes) -> bytes:
    return F6(data)

def F7(data: bytes) -> bytes:
    # NOT bitwise, autoinverso
    return bytes((~b) & 0xFF for b in data)

def inv_F7(data: bytes) -> bytes:
    return F7(data)

def F8(data: bytes) -> bytes:
    # rotar cada byte a la izquierda 3 (inversa: ror 3)
    return bytes(rol_byte(b,3) for b in data)

def inv_F8(data: bytes) -> bytes:
    return bytes(ror_byte(b,3) for b in data)


# Mapeos para uso dinámico:
FUNC_MAP = {
    1: (F1, inv_F1),
    2: (F2, inv_F2),
    3: (F3, inv_F3),
    4: (F4, inv_F4),
    5: (F5, inv_F5),
    6: (F6, inv_F6),
    7: (F7, inv_F7),
    8: (F8, inv_F8),
}

def apply_sequence(data: bytes, func_ids: list) -> bytes:
    for fid in func_ids:
        f, _ = FUNC_MAP[fid]
        data = f(data)
    return data

def undo_sequence(data: bytes, func_ids: list) -> bytes:
    # aplicar inversas en orden inverso
    for fid in reversed(func_ids):
        _, inv = FUNC_MAP[fid]
        data = inv(data)
    return data

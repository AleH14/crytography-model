# PSN.py
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from ReversibleFunctions import apply_sequence, undo_sequence

# Esquemas
ESQUEMAS = {
    0x0: {"func_ids": [1,2,3,4], "next_extraction": {"type":"byte_index","param":0}},   # primer byte
    0x1: {"func_ids": [1,3,5],   "next_extraction": {"type":"last_byte","param":None}}, # último byte
    0x2: {"func_ids": [2,4,6,8], "next_extraction": {"type":"slice","param":(1,1)}},   # byte en offset 1 longitud 1
    0x3: {"func_ids": [8,7],     "next_extraction": {"type":"bit_pos","param":(0,4)}},  # nibble 0..3 of byte 0
    0x4: {"func_ids": [1,5],     "next_extraction": {"type":"byte_index","param":2}},
    0x5: {"func_ids": [3,6,1],   "next_extraction": {"type":"last_byte","param":None}},
    0x6: {"func_ids": [4,2],     "next_extraction": {"type":"slice","param":(0,2)}},
    0x7: {"func_ids": [6,3,8],   "next_extraction": {"type":"byte_index","param":1}},
    0x8: {"func_ids": [7,1,4],   "next_extraction": {"type":"slice","param":(2,1)}},
    0x9: {"func_ids": [2,8],     "next_extraction": {"type":"byte_index","param":3}},
    0xA: {"func_ids": [3,1,6,7], "next_extraction": {"type":"last_byte","param":None}},
    0xB: {"func_ids": [4,8,2],   "next_extraction": {"type":"bit_pos","param":(1,4)}},
    0xC: {"func_ids": [5,7,3],   "next_extraction": {"type":"slice","param":(0,1)}},
    0xD: {"func_ids": [6,2,1],   "next_extraction": {"type":"byte_index","param":4}},
    0xE: {"func_ids": [7,4],     "next_extraction": {"type":"slice","param":(4,1)}},
    0xF: {"func_ids": [8,5,1,3], "next_extraction": {"type":"byte_index","param":5}},
}

def pack_payload_with_psn(psn: int, processed_plaintext: bytes) -> bytes:
    if not (0 <= psn <= 0xF):
        raise ValueError("PSN debe estar entre 0 y 15 (4 bits)")
    psn_byte = psn & 0x0F
    return bytes([psn_byte]) + processed_plaintext

def unpack_psn_and_payload(payload: bytes):
    if len(payload) == 0:
        raise ValueError("Payload vacío")
    psn = payload[0] & 0x0F
    data = payload[1:]
    return psn, data

def encrypt_message(plaintext: bytes, psn: int, key: bytes) -> bytes:
    # key: 8 bytes (64 bits) de KeyGenerator
    # Convertir a 16 bytes para AES-128 (concatenar con sí mismo)
    aes_key = key + key  # 16 bytes para AES-128
    
    scheme = ESQUEMAS[psn]
    func_ids = scheme["func_ids"]
    processed = apply_sequence(plaintext, func_ids)
    payload = pack_payload_with_psn(psn, processed)
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)  # 96-bit recommended for GCM
    ciphertext = aesgcm.encrypt(nonce, payload, associated_data=None)
    # mensaje final: nonce || ciphertext
    return nonce + ciphertext

def decrypt_message(message: bytes, key: bytes):
    # key: 8 bytes (64 bits) de KeyGenerator
    # Convertir a 16 bytes para AES-128 (concatenar con sí mismo)
    aes_key = key + key  # 16 bytes para AES-128
    
    if len(message) < 12:
        raise ValueError("Mensaje demasiado corto (esperado nonce + ciphertext)")
    nonce = message[:12]
    ciphertext = message[12:]
    aesgcm = AESGCM(aes_key)
    payload = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
    psn, processed = unpack_psn_and_payload(payload)
    scheme = ESQUEMAS[psn]
    func_ids = scheme["func_ids"]
    plaintext = undo_sequence(processed, func_ids)
    return {
        "psn": psn,
        "plaintext": plaintext,
        "next_extraction_instruction": scheme["next_extraction"],
    }

def extract_psn_from_plaintext_using_instruction(plaintext: bytes, instruction: dict) -> int:
    t = instruction["type"]
    p = instruction.get("param")
    if t == "byte_index":
        idx = p
        if idx < 0 or idx >= len(plaintext):
            raise IndexError("byte_index fuera de rango")
        return plaintext[idx] & 0x0F
    elif t == "last_byte":
        return plaintext[-1] & 0x0F
    elif t == "slice":
        start, length = p
        if start < 0 or start+length > len(plaintext):
            raise IndexError("slice fuera de rango")
        return plaintext[start] & 0x0F
    elif t == "bit_pos":
        byte_index, nib_idx = p
        b = plaintext[byte_index]
        if nib_idx == 0:
            return b & 0x0F
        else:
            return (b >> 4) & 0x0F
    else:
        raise ValueError("Instrucción desconocida")
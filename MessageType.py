# Message.py
# ------------------------------------------------------------
# Construye mensajes estructurados para el sistema criptográfico.
# Compatible con tipos: RM, FCM, KUM, LCM.
# ------------------------------------------------------------

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from KeyGenerator import generate_key_table
from SeedAndPrimes import SharedParams
import time

# ------------------------------------------------------------
# Enumeración de tipos de mensajes
# ------------------------------------------------------------

from enum import Enum, auto

class MessageType(Enum):
    FCM = auto()  # Full Cipher Message
    RM = auto()   # Request Message
    KUM = auto()  # Key Update Message
    LCM = auto()  # Last Cipher Message

    def __str__(self):
        return self.name

# ------------------------------------------------------------
# Clase principal de mensaje
# ------------------------------------------------------------

@dataclass
class Message:
    tipo: str               # Tipo de mensaje: "RM", "FCM", etc.
    contenido: str          # Texto plano o cifrado
    psn: int                # Número de secuencia
    p: int                  # Primo local
    s: int                  # Semilla compartida
    q: int                  # Primo remoto
    n: int = 4              # Número de llaves (por defecto 4)

    def build(self) -> Dict[str, Any]:
        """Construye el mensaje completo listo para enviar"""
        if self.tipo not in MessageType.__members__:
            raise ValueError(f"Tipo de mensaje inválido: {self.tipo}")

        tipo_enum = MessageType[self.tipo]

        # Generar llaves si el tipo lo requiere
        keys: Optional[List[int]] = None
        if tipo_enum in [MessageType.FCM, MessageType.KUM]:
            shared = SharedParams(id=self.p, P=self.p, Q=self.q, S=self.s, N=self.n)
            keys = generate_key_table(shared, n_keys=self.n)

        # Construir el payload
        return {
            "tipo": tipo_enum.name,
            "contenido": self.contenido,
            "psn": self.psn,
            "sender_id": self.p,
            "keys": keys,
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "status": "OK"
            }
        }

    def __str__(self):
        return f"[{self.tipo}] PSN={self.psn} | Contenido={self.contenido[:30]}..."# Message.py
# ------------------------------------------------------------
# Construye mensajes estructurados para el sistema criptográfico.
# Compatible con tipos: RM, FCM, KUM, LCM.
# ------------------------------------------------------------

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from KeyGenerator import generate_key_table
from SeedAndPrimes import SharedParams
import time

# ------------------------------------------------------------
# Enumeración de tipos de mensajes
# ------------------------------------------------------------

from enum import Enum, auto

class MessageType(Enum):
    FCM = auto()  # Full Cipher Message
    RM = auto()   # Request Message
    KUM = auto()  # Key Update Message
    LCM = auto()  # Last Cipher Message

    def __str__(self):
        return self.name

# ------------------------------------------------------------
# Clase principal de mensaje
# ------------------------------------------------------------

@dataclass
class Message:
    tipo: str               # Tipo de mensaje: "RM", "FCM", etc.
    contenido: str          # Texto plano o cifrado
    psn: int                # Número de secuencia
    p: int                  # Primo local
    s: int                  # Semilla compartida
    q: int                  # Primo remoto
    n: int = 4              # Número de llaves (por defecto 4)

    def build(self) -> Dict[str, Any]:
        """Construye el mensaje completo listo para enviar"""
        if self.tipo not in MessageType.__members__:
            raise ValueError(f"Tipo de mensaje inválido: {self.tipo}")

        tipo_enum = MessageType[self.tipo]

        # Generar llaves si el tipo lo requiere
        keys: Optional[List[int]] = None
        if tipo_enum in [MessageType.FCM, MessageType.KUM]:
            shared = SharedParams(id=self.p, P=self.p, Q=self.q, S=self.s, N=self.n)
            keys = generate_key_table(shared, n_keys=self.n)

        # Construir el payload
        return {
            "tipo": tipo_enum.name,
            "contenido": self.contenido,
            "psn": self.psn,
            "sender_id": self.p,
            "keys": keys,
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "status": "OK"
            }
        }

    def __str__(self):
        return f"[{self.tipo}] PSN={self.psn} | Contenido={self.contenido[:30]}..."
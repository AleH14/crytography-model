"""
MessageTypes.py
---------------
Define los tipos de mensajes del sistema de cifrado polimórfico.
Cada mensaje tiene un propósito específico en el protocolo de comunicación.
"""

from enum import Enum

class MessageType(Enum):
    """Tipos de mensajes del protocolo"""
    FCM = "FCM"  # First Contact Message - Primer mensaje de contacto
    RM = "RM"    # Regular Message - Mensaje regular encriptado
    KUM = "KUM"  # Key Update Message - Actualización de tabla de llaves
    LCM = "LCM"  # Last Contact Message - Último mensaje de contacto

# Descripciones de los tipos de mensaje
MESSAGE_DESCRIPTIONS = {
    MessageType.FCM: {
        "name": "First Contact Message",
        "description": "Establece la conexión inicial e intercambia parámetros criptográficos (P, Q, S)",
        "icon": "🤝",
        "color": "#0078d4"
    },
    MessageType.RM: {
        "name": "Regular Message", 
        "description": "Mensaje cifrado usando PSN y tabla de llaves actual",
        "icon": "💬",
        "color": "#107c10"
    },
    MessageType.KUM: {
        "name": "Key Update Message",
        "description": "Regenera las tablas de llaves cuando se agotan",
        "icon": "🔄",
        "color": "#ff8c00"
    },
    MessageType.LCM: {
        "name": "Last Contact Message",
        "description": "Cierra la conexión y elimina las tablas de llaves",
        "icon": "👋",
        "color": "#d13438"
    }
}

def get_message_info(msg_type: MessageType):
    """Obtener información detallada de un tipo de mensaje"""
    return MESSAGE_DESCRIPTIONS.get(msg_type, {
        "name": "Unknown",
        "description": "Tipo de mensaje desconocido",
        "icon": "❓",
        "color": "#888888"
    })

def format_message_log(msg_type: MessageType, additional_info: str = ""):
    """Formatear mensaje para el log"""
    info = get_message_info(msg_type)
    base_msg = f"{info['icon']} {msg_type.value} - {info['name']}"
    if additional_info:
        base_msg += f": {additional_info}"
    return base_msg

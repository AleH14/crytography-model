# crytography-model


---

## 📜 Descripción de Archivos

### `SeedAndPrimes.py`
- Genera los parámetros iniciales:
  - Semilla `S`
  - Números primos `P` y `Q`
  - Identificadores de nodos

---

### `KeyGenerator.py`
- Implementa la **generación de llaves dinámicas**.
- Calcula funciones:
  - `fs`, `fg`, `fm`
- Construye la **tabla de llaves** para cifrado y descifrado.

---

### `ReversibleFunctions.py`
- Define las **funciones polimórficas reversibles**:
  - `f(x)` → transformación
  - `inv_f(x)` → transformación inversa  

Estas garantizan que el cifrado sea reversible.

---

### `PSN.py`
- Implementa el **Polymorphic Sequence Nibble (PSN)**:
  - Generación de secuencias pseudoaleatorias.
  - Variación dinámica en cada sesión.

---

### `MessageTypes.py`
- Define una enumeración / clase para los **tipos de mensajes**:
  - `FCM` → Full Cipher Message  
  - `RM` → Request Message  
  - `KUM` → Key Update Message  
  - `LCM` → Last Cipher Message  

---

### `client.py`
- GUI para el cliente.
- Responsable de:
  - Cifrar mensajes.
  - Enviar datos al servidor.

---

### `server.py`
- GUI para el servidor.
- Responsable de:
  - Recibir mensajes cifrados.
  - Descifrar y mostrar resultados.

---


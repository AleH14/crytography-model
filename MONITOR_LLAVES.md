# 🔑 Monitor de Llaves - Nueva Funcionalidad

## ✨ **Características Implementadas**

### 🖥️ **Cliente**
- **Botón "Monitor Llaves"** en la interfaz principal
- **Ventana de monitoreo** que muestra:
  - Tabla completa de 16 llaves (K00-K15)
  - Hash visual de cada llave (sin revelar valores reales)
  - Estado actual de cada llave:
    - 🎯 **ACTUAL** - Llave que se usará próximamente
    - ✅ **Usada** - Llaves ya utilizadas
    - 🔑 **Disponible** - Llaves pendientes por usar
  - Información de sincronización:
    - Llave actual (Kxx)
    - PSN actual
- **Actualización automática** cada segundo
- **Resaltado visual** de la llave activa

### 🖥️ **Servidor**
- **Botón "Monitor Llaves"** (disponible cuando está ejecutándose)
- **Selector de cliente** para monitorear múltiples conexiones
- **Misma visualización** que el cliente
- **Sincronización independiente** por cada cliente conectado
- **Actualización en tiempo real** del estado de llaves

## 🔐 **Seguridad**

### **Información NO Revelada:**
- ❌ Valores reales de las llaves (64 bits)
- ❌ Contenido de los mensajes cifrados
- ❌ Algoritmos internos de generación

### **Información Mostrada (Segura):**
- ✅ Hash visual de 8 caracteres (no reversible)
- ✅ Índice de llave actual
- ✅ Estado de uso (usada/actual/disponible)
- ✅ Valor PSN actual
- ✅ Sincronización entre cliente y servidor

## 📊 **Estados Visuales**

| Estado | Emoji | Color | Descripción |
|--------|-------|-------|-------------|
| Actual | 🎯 | Amarillo | Llave que se usará en el próximo mensaje |
| Usada | ✅ | Gris | Llave ya utilizada en mensajes anteriores |
| Disponible | 🔑 | Verde | Llave pendiente por utilizar |

## 🚀 **Cómo Usar**

### **En el Cliente:**
1. Conectar al servidor
2. Hacer clic en **"Monitor Llaves"**
3. Observar la sincronización mientras se envían mensajes
4. La ventana se actualiza automáticamente

### **En el Servidor:**
1. Iniciar el servidor
2. Esperar conexiones de clientes
3. Hacer clic en **"Monitor Llaves"**
4. Seleccionar cliente a monitorear del dropdown
5. Observar sincronización en tiempo real

## 🎯 **Funcionalidad de Sincronización**

### **Proceso:**
1. **Inicio**: Ambos generan la misma tabla de 16 llaves
2. **Envío**: Cliente usa llave actual (ej: K05)
3. **Recepción**: Servidor usa la misma llave (K05)
4. **Avance**: Ambos incrementan índice (K05 → K06)
5. **Repetición**: Proceso continúa hasta K15
6. **Regeneración**: Al agotar las 16 llaves, se genera nueva tabla

### **Visualización:**
- **Monitor del cliente** muestra su estado local
- **Monitor del servidor** muestra el estado de cada cliente
- **Sincronización visual** demuestra que ambos usan las mismas llaves
- **Hash visual** permite verificar que las llaves coinciden sin revelar valores

## 🔄 **Actualización Automática**

- **Frecuencia**: Cada 1 segundo
- **Información actualizada**:
  - Índice de llave actual
  - Valor PSN actual
  - Estados visuales de todas las llaves
  - Lista de clientes conectados (servidor)

## 💡 **Beneficios**

1. **Transparencia**: Ver cómo funciona la sincronización
2. **Debugging**: Identificar problemas de sincronización
3. **Educativo**: Entender el algoritmo polimórfico
4. **Seguridad**: Sin revelar información sensible
5. **Tiempo Real**: Monitoreo en vivo del proceso

¡Ahora puedes ver exactamente cómo se sincronizan las llaves entre cliente y servidor sin comprometer la seguridad del sistema!

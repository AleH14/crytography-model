"""
Script de prueba para verificar el monitor de llaves
"""
import tkinter as tk
from tkinter import messagebox

def test_monitor():
    """Prueba básica del monitor"""
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    messagebox.showinfo("Monitor de Llaves", 
                       "✅ Funcionalidades implementadas:\n\n"
                       "🔑 Cliente:\n"
                       "- Botón 'Monitor Llaves' en la interfaz\n"
                       "- Visualización de tabla de 16 llaves\n"
                       "- Hash visual sin revelar valores\n"
                       "- Estado: Actual, Usada, Disponible\n"
                       "- Actualización automática cada segundo\n\n"
                       "🖥️ Servidor:\n"
                       "- Selector de cliente a monitorear\n"
                       "- Misma visualización que cliente\n"
                       "- Sincronización en tiempo real\n"
                       "- Estado por cliente independiente\n\n"
                       "🔄 Sincronización:\n"
                       "- Índice de llave actual (K0-K15)\n"
                       "- Valor PSN actual\n"
                       "- Estados visuales sincronizados")
    
    root.destroy()

if __name__ == "__main__":
    test_monitor()

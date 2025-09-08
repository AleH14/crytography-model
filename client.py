import socket
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from PSN import encrypt_message, decrypt_message, extract_psn_from_plaintext_using_instruction
from SeedAndPrimes import generate_prime, generate_seed, generate_node_id
from KeyGenerator import generate_key_table
from MessageTypes import MessageType, get_message_info, format_message_log
from dataclasses import dataclass

@dataclass
class SharedParams:
    id: int
    P: int
    Q: int
    S: int
    N: int = 16  # Número de llaves a generar

class CryptographyClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cryptography Client")
        self.root.geometry("600x500")
        self.root.configure(bg='#2b2b2b')
        self.root.resizable(True, True)
        
        # Configuración de estilo
        self.setup_styles()
        
        # Variables
        self.client_socket = None
        self.connected = False
        self.host = "127.0.0.1"
        self.port = 65432
        
        # Generar parámetros del cliente
        self.node_id = generate_node_id(tag="client")
        self.P = generate_prime(tag="client")  # Primo del cliente
        self.S_client = generate_seed(tag="client")  # Semilla del cliente
        
        # Variables para el estado de cifrado
        self.key_table = []
        self.key_index = 0
        self.next_psn = 0
        self.next_extraction_instruction = None
        self.encryption_enabled = True  # Control de cifrado
        self.key_regeneration_count = 0  # Contador de regeneraciones
        
        # Variables para monitoreo visual
        self.key_monitor_window = None
        self.key_status_vars = []
        self.key_labels = []
        
        # Crear la interfaz inicial
        self.create_initial_interface()
        
        # Configurar el cierre de la ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_styles(self):
        """Configurar estilos para una apariencia profesional"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configurar colores personalizados
        self.style.configure('Title.TLabel',
                           font=('Arial', 16, 'bold'),
                           foreground='white',
                           background='#2b2b2b')
        
        self.style.configure('Connect.TButton',
                           font=('Arial', 12, 'bold'),
                           foreground='white',
                           background='#0078d4',
                           borderwidth=0,
                           focuscolor='none')
        
        self.style.map('Connect.TButton',
                      background=[('active', '#106ebe')])
        
        self.style.configure('Disconnect.TButton',
                           font=('Arial', 10, 'bold'),
                           foreground='white',
                           background='#d13438',
                           borderwidth=0,
                           focuscolor='none')
        
        self.style.map('Disconnect.TButton',
                      background=[('active', '#b52529')])
        
        self.style.configure('Send.TButton',
                           font=('Arial', 10, 'bold'),
                           foreground='white',
                           background='#107c10',
                           borderwidth=0,
                           focuscolor='none')
        
        self.style.map('Send.TButton',
                      background=[('active', '#0e6e0e')])
        
        # Estilo para botón de cifrado (activado)
        self.style.configure('Encrypt.TButton',
                           font=('Arial', 10, 'bold'),
                           foreground='white',
                           background='#107c10',
                           borderwidth=0,
                           focuscolor='none')
        
        self.style.map('Encrypt.TButton',
                      background=[('active', '#0e6e0e')])
        
        # Estilo para botón de cifrado (desactivado)
        self.style.configure('Decrypt.TButton',
                           font=('Arial', 10, 'bold'),
                           foreground='white',
                           background='#d13438',
                           borderwidth=0,
                           focuscolor='none')
        
        self.style.map('Decrypt.TButton',
                      background=[('active', '#b52529')])
    
    def create_initial_interface(self):
        """Crear la pantalla inicial con el botón de conexión"""
        self.initial_frame = tk.Frame(self.root, bg='#2b2b2b')
        self.initial_frame.pack(expand=True, fill='both')
        
        # Logo/Título
        title_label = ttk.Label(self.initial_frame, 
                               text="🔐 Cryptography Client",
                               style='Title.TLabel')
        title_label.pack(pady=(100, 30))
        
        # Subtítulo
        subtitle_label = ttk.Label(self.initial_frame,
                                 text="Secure Communication Client",
                                 font=('Arial', 10),
                                 foreground='#cccccc',
                                 background='#2b2b2b')
        subtitle_label.pack(pady=(0, 50))
        
        # Botón de conexión
        connect_button = ttk.Button(self.initial_frame,
                                  text="Establecer comunicación con el servidor\n(First Message Contact)",
                                  style='Connect.TButton',
                                  command=self.connect_to_server)
        connect_button.pack(pady=20, padx=50, ipady=15)
        
        # Información de conexión
        info_frame = tk.Frame(self.initial_frame, bg='#2b2b2b')
        info_frame.pack(pady=(50, 0))
        
        info_label = ttk.Label(info_frame,
                             text=f"Conectando a: {self.host}:{self.port}",
                             font=('Arial', 9),
                             foreground='#888888',
                             background='#2b2b2b')
        info_label.pack()
    
    def connect_to_server(self):
        """Conectar al servidor y cambiar a la interfaz de chat"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.connected = True
            
            # Cambiar a la interfaz de chat PRIMERO
            self.create_chat_interface()
            
            # Ahora mostrar mensaje FCM
            fcm_msg = format_message_log(MessageType.FCM, "Enviando parámetros P y S al servidor")
            self.add_message_to_chat("Sistema", fcm_msg, get_message_info(MessageType.FCM)["color"])
            
            # Enviar parámetros del cliente al servidor
            client_params = f"{self.P},{self.S_client}"
            self.client_socket.sendall(client_params.encode())
            
            # Recibir parámetros del servidor
            server_params = self.client_socket.recv(1024).decode()
            Q_server, S_server = map(int, server_params.split(','))
            
            # Confirmar FCM completado
            fcm_complete = format_message_log(MessageType.FCM, "Parámetros intercambiados exitosamente")
            self.add_message_to_chat("Sistema", fcm_complete, get_message_info(MessageType.FCM)["color"])
            
            # Calcular semilla compartida
            S_shared = self.S_client ^ S_server
            
            # Crear parámetros compartidos
            shared_params = SharedParams(
                id=self.node_id,
                P=self.P,
                Q=Q_server,
                S=S_shared
            )
            
            # Generar tabla de claves
            self.key_table = generate_key_table(shared_params)
            self.key_index = 0
            
            # Enviar mensaje inicial encriptado
            initial_message = b"First Message Contact"
            key = self.key_table[self.key_index].to_bytes(8, 'big')
            self.add_message_to_chat("Debug", f"Cliente enviando FCM: PSN={self.next_psn}, Key=K{self.key_index}", "#888888")
            ciphertext = encrypt_message(initial_message, self.next_psn, key)
            self.client_socket.sendall(ciphertext)
            
            # ¡CORRECCIÓN! El cliente debe calcular PSN basándose en SU mensaje enviado, no en la respuesta
            # Esto mantiene la sincronización con el servidor
            old_psn = self.next_psn
            old_key_index = self.key_index
            
            # Actualizar PSN basándose en el mensaje que ENVIAMOS (como hace el servidor)
            instruction = {"type": "byte_index", "param": 0}  # Esquema por defecto para PSN=0
            self.next_psn = extract_psn_from_plaintext_using_instruction(initial_message, instruction)
            self.next_extraction_instruction = instruction
            
            # Actualizar índice de llave
            self.key_index = (self.key_index + 1) % len(self.key_table)
            
            self.add_message_to_chat("Debug", f"Cliente después FCM: PSN {old_psn}→{self.next_psn}, Key K{old_key_index}→K{self.key_index}", "#888888")
            
            # Recibir respuesta (solo para confirmar, no para actualizar estado)
            response = self.client_socket.recv(2048)
            result = decrypt_message(response, key)
            server_response = result["plaintext"].decode()
            self.add_message_to_chat("Debug", f"Respuesta del servidor: '{server_response}'", "#888888")
            
            # Agregar mensajes de bienvenida
            self.add_message_to_chat("Sistema", "Conexión establecida correctamente", "#107c10")
            self.add_message_to_chat("Sistema", "🔐 Modo cifrado activado - Los mensajes se envían encriptados", "#107c10")
            
            # Inicializar el monitor de llaves
            self.init_key_monitor_data()
            
            # Iniciar hilo para recibir mensajes
            self.start_receiving_thread()
            
        except Exception as e:
            messagebox.showerror("Error de Conexión", 
                               f"No se pudo conectar al servidor:\n{str(e)}")
    
    def create_chat_interface(self):
        """Crear la interfaz de chat"""
        # Ocultar la pantalla inicial
        self.initial_frame.destroy()
        
        # Frame principal del chat
        self.chat_frame = tk.Frame(self.root, bg='#2b2b2b')
        self.chat_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Header con botón de desconexión
        header_frame = tk.Frame(self.chat_frame, bg='#2b2b2b')
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Título del chat
        chat_title = ttk.Label(header_frame,
                             text="🔐 Comunicación Segura",
                             font=('Arial', 16, 'bold'),
                             foreground='#ffffff',
                             background='#2b2b2b')
        chat_title.pack(side='left')
        
        # Estado de conexión
        self.status_label = ttk.Label(header_frame,
                                    text="● Conectado",
                                    font=('Arial', 11, 'bold'),
                                    foreground='#00ff00',
                                    background='#2b2b2b')
        self.status_label.pack(side='left', padx=(10, 0))
        
        # Botón de monitoreo de llaves
        monitor_button = ttk.Button(header_frame,
                                  text="Monitor Llaves",
                                  style='Send.TButton',
                                  command=self.show_key_monitor)
        monitor_button.pack(side='right', padx=(0, 10))
        
        # Botón de desconexión
        disconnect_button = ttk.Button(header_frame,
                                     text="Cerrar conexión\n(Last Message Contact)",
                                     style='Disconnect.TButton',
                                     command=self.disconnect_from_server)
        disconnect_button.pack(side='right')
        
        # Área de mensajes
        self.chat_area = scrolledtext.ScrolledText(self.chat_frame,
                                                  width=70,
                                                  height=20,
                                                  bg='#1e1e1e',
                                                  fg='#ffffff',
                                                  font=('Consolas', 12, 'bold'),
                                                  state='disabled',
                                                  wrap='word',
                                                  borderwidth=2,
                                                  relief='solid')
        self.chat_area.pack(expand=True, fill='both', pady=(0, 10))
        
        # Frame para entrada de mensaje
        input_frame = tk.Frame(self.chat_frame, bg='#2b2b2b')
        input_frame.pack(fill='x')
        
        # Campo de entrada de mensaje
        self.message_entry = tk.Entry(input_frame,
                                    font=('Arial', 13, 'bold'),
                                    bg='#3c3c3c',
                                    fg='#ffffff',
                                    insertbackground='#00ff00',
                                    borderwidth=2,
                                    relief='solid')
        self.message_entry.pack(side='left', expand=True, fill='x', padx=(0, 10))
        self.message_entry.bind('<Return>', self.send_message)
        
        # Botón de cifrado/descifrado
        self.encrypt_button = ttk.Button(input_frame,
                                       text="🔐 Cifrar",
                                       style='Encrypt.TButton',
                                       command=self.toggle_encryption)
        self.encrypt_button.pack(side='right', padx=(0, 5))
        
        # Botón de enviar
        send_button = ttk.Button(input_frame,
                               text="Enviar",
                               style='Send.TButton',
                               command=self.send_message)
        send_button.pack(side='right')
        
        # Enfocar el campo de entrada
        self.message_entry.focus()
    
    def add_message_to_chat(self, sender, message, color="#ffffff"):
        """Agregar un mensaje al área de chat"""
        self.chat_area.config(state='normal')
        
        # Agregar timestamp
        timestamp = time.strftime("%H:%M:%S")
        
        # Agregar el mensaje
        self.chat_area.insert(tk.END, f"[{timestamp}] {sender}: {message}\n")
        
        # Configurar color si es necesario
        if color != "#ffffff":
            start_index = self.chat_area.index("end-2l linestart")
            end_index = self.chat_area.index("end-1l")
            self.chat_area.tag_add("colored", start_index, end_index)
            self.chat_area.tag_config("colored", foreground=color)
        
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)
    
    def toggle_encryption(self):
        """Alternar entre modo cifrado y texto claro"""
        self.encryption_enabled = not self.encryption_enabled
        
        if self.encryption_enabled:
            self.encrypt_button.config(text="🔐 Cifrar", style='Encrypt.TButton')
            self.add_message_to_chat("Sistema", "🔐 Modo cifrado activado - Los mensajes se envían encriptados", "#107c10")
        else:
            self.encrypt_button.config(text="🔓 Texto Claro", style='Decrypt.TButton')
            self.add_message_to_chat("Sistema", "🔓 Modo texto claro activado - Los mensajes se envían sin cifrar", "#d13438")
    
    def send_message(self, event=None):
        """Enviar mensaje al servidor"""
        if not self.connected:
            return
            
        message = self.message_entry.get().strip()
        if not message:
            return
        
        try:
            if self.encryption_enabled:
                # Verificar si necesitamos regenerar llaves
                if self.key_index == 0 and self.key_regeneration_count > 0:
                    kum_msg = format_message_log(MessageType.KUM, f"Regenerando tabla de llaves (ciclo #{self.key_regeneration_count + 1})")
                    self.add_message_to_chat("Sistema", kum_msg, get_message_info(MessageType.KUM)["color"])
                
                # Mostrar mensaje RM
                rm_msg = format_message_log(MessageType.RM, f"Enviando con llave K{self.key_index:02d}, PSN={self.next_psn}")
                self.add_message_to_chat("Sistema", rm_msg, get_message_info(MessageType.RM)["color"])
                
                # Modo cifrado: usar el algoritmo de cifrado polimórfico
                key = self.key_table[self.key_index].to_bytes(8, 'big')
                message_bytes = message.encode()
                ciphertext = encrypt_message(message_bytes, self.next_psn, key)
                self.client_socket.sendall(ciphertext)
                
                # ¡CORRECCIÓN CRÍTICA! Actualizar PSN basándose en el mensaje enviado (como hace el servidor)
                old_psn = self.next_psn
                old_key_index = self.key_index
                
                # Usar la instrucción de extracción actual para calcular el próximo PSN
                if self.next_extraction_instruction:
                    self.next_psn = extract_psn_from_plaintext_using_instruction(
                        message_bytes, 
                        self.next_extraction_instruction
                    )
                else:
                    # Usar esquema por defecto si no hay instrucción
                    instruction = {"type": "byte_index", "param": 0}
                    self.next_psn = extract_psn_from_plaintext_using_instruction(message_bytes, instruction)
                
                # Actualizar índice de llave
                self.key_index = (self.key_index + 1) % len(self.key_table)
                
                # Debug: mostrar actualización
                self.add_message_to_chat("Debug", f"Cliente actualizó: PSN {old_psn}→{self.next_psn}, Key K{old_key_index}→K{self.key_index}", "#888888")
                
                # Si volvemos al inicio, incrementar contador de regeneración
                if old_key_index == len(self.key_table) - 1:
                    self.key_regeneration_count += 1
                
                # Agregar mensaje al chat con indicador de cifrado
                self.add_message_to_chat("Tú 🔐", message, "#0078d4")
            else:
                # Modo texto claro: enviar con prefijo especial
                plaintext_message = f"[PLAINTEXT]{message}"
                self.client_socket.sendall(plaintext_message.encode())
                
                # Agregar mensaje al chat con indicador de texto claro
                self.add_message_to_chat("Tú 🔓", message, "#ff9900")
            
            # Limpiar campo de entrada
            self.message_entry.delete(0, tk.END)
            
        except Exception as e:
            self.add_message_to_chat("Error", f"No se pudo enviar el mensaje: {str(e)}", "#d13438")
    
    def start_receiving_thread(self):
        """Iniciar hilo para recibir mensajes del servidor"""
        receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        receive_thread.start()
    
    def receive_messages(self):
        """Recibir mensajes del servidor en un hilo separado"""
        while self.connected:
            try:
                response = self.client_socket.recv(2048)
                if response:
                    # Verificar si es un mensaje broadcast (no encriptado)
                    if response.startswith(b"[BROADCAST]"):
                        message = response.decode()[12:]  # Remover prefijo [BROADCAST] 
                        self.root.after(0, lambda msg=message: self.add_message_to_chat("📢 Broadcast", msg, "#ff9900"))
                        continue
                    
                    # Verificar si es un mensaje en texto claro
                    if response.startswith(b"[PLAINTEXT]"):
                        message = response.decode()[11:]  # Remover prefijo [PLAINTEXT]
                        self.root.after(0, lambda msg=message: self.add_message_to_chat("Servidor 🔓", msg, "#ff9900"))
                        continue
                    
                    # Mensaje cifrado - desencriptar
                    key = self.key_table[self.key_index].to_bytes(8, 'big')
                    
                    result = decrypt_message(response, key)
                    message = result["plaintext"].decode()
                    
                    # Actualizar próximo PSN
                    self.next_psn = extract_psn_from_plaintext_using_instruction(
                        result["plaintext"], 
                        result["next_extraction_instruction"]
                    )
                    self.next_extraction_instruction = result["next_extraction_instruction"]
                    
                    # Actualizar índice de clave
                    self.key_index = (self.key_index + 1) % len(self.key_table)
                    
                    # Mostrar mensaje cifrado
                    self.root.after(0, lambda msg=message: self.add_message_to_chat("Servidor 🔐", msg, "#ffb900"))
                else:
                    break
            except Exception as e:
                if self.connected:
                    error_msg = f"Error recibiendo mensaje: {str(e)}"
                    self.root.after(0, lambda msg=error_msg: self.add_message_to_chat("Error", msg, "#d13438"))
                break
    
    def disconnect_from_server(self):
        """Desconectar del servidor"""
        if self.connected and self.client_socket:
            try:
                # Verificar que tengamos una tabla de llaves válida
                if not self.key_table or self.key_index >= len(self.key_table):
                    # Si no hay tabla de llaves, desconectar sin cifrado
                    self.add_message_to_chat("Sistema", "⚠️ Desconectando sin tabla de llaves válida", "#ff8c00")
                    self.connected = False
                    self.client_socket.close()
                    self.status_label.config(text="● Desconectado", foreground="#d13438")
                    return
                
                # Mostrar mensaje LCM
                lcm_msg = format_message_log(MessageType.LCM, "Cerrando conexión y eliminando tabla de llaves")
                self.add_message_to_chat("Sistema", lcm_msg, get_message_info(MessageType.LCM)["color"])
                
                # Obtener clave actual
                key = self.key_table[self.key_index].to_bytes(8, 'big')
                
                # Enviar mensaje de despedida encriptado
                farewell_message = b"Last Message Contact"
                ciphertext = encrypt_message(farewell_message, self.next_psn, key)
                self.client_socket.sendall(ciphertext)
                
                # Recibir confirmación con timeout
                self.client_socket.settimeout(5.0)  # 5 segundos de timeout
                try:
                    response = self.client_socket.recv(2048)
                    if response:
                        result = decrypt_message(response, key)
                        message = result["plaintext"].decode()
                        self.add_message_to_chat("Sistema", f"Respuesta del servidor: {message}", "#d13438")
                    else:
                        self.add_message_to_chat("Sistema", "Servidor desconectado sin respuesta", "#ff8c00")
                except socket.timeout:
                    self.add_message_to_chat("Sistema", "Timeout esperando respuesta del servidor", "#ff8c00")
                except Exception as recv_error:
                    self.add_message_to_chat("Sistema", f"Error recibiendo respuesta: {str(recv_error)}", "#ff8c00")
                
                # Limpiar estado
                self.connected = False
                if self.client_socket:
                    self.client_socket.close()
                    self.client_socket = None
                
                # Eliminar tabla de llaves (LCM completado)
                self.key_table = []
                self.key_index = 0
                self.key_regeneration_count = 0
                
                lcm_complete = format_message_log(MessageType.LCM, "Tabla de llaves eliminada, conexión cerrada")
                self.add_message_to_chat("Sistema", lcm_complete, get_message_info(MessageType.LCM)["color"])
                
                # Actualizar estado
                if hasattr(self, 'status_label'):
                    self.status_label.config(text="● Desconectado", foreground="#d13438")
                
                # Mostrar mensaje y cerrar después de 2 segundos
                self.root.after(2000, self.root.quit)
                
            except Exception as e:
                error_msg = f"Error al desconectar: {str(e)}"
                if hasattr(self, 'chat_area'):
                    self.add_message_to_chat("Error", error_msg, "#d13438")
                else:
                    messagebox.showerror("Error", error_msg)
                
                # Forzar limpieza en caso de error
                self.connected = False
                if self.client_socket:
                    try:
                        self.client_socket.close()
                    except:
                        pass
                    self.client_socket = None
        else:
            # No hay conexión activa
            if hasattr(self, 'chat_area'):
                self.add_message_to_chat("Sistema", "No hay conexión activa para cerrar", "#ff8c00")
            else:
                messagebox.showinfo("Info", "No hay conexión activa para cerrar")
    
    def init_key_monitor_data(self):
        """Inicializar datos para el monitor de llaves"""
        if self.key_table:
            self.key_status_vars = []
            for i in range(len(self.key_table)):
                status = "🔑 Disponible" if i != self.key_index else "🎯 Actual"
                self.key_status_vars.append(status)
    
    def show_key_monitor(self):
        """Mostrar ventana de monitoreo de llaves"""
        if self.key_monitor_window is not None and self.key_monitor_window.winfo_exists():
            self.key_monitor_window.lift()
            return
        
        self.key_monitor_window = tk.Toplevel(self.root)
        self.key_monitor_window.title("🔑 Monitor de Llaves - Cliente")
        self.key_monitor_window.geometry("600x500")
        self.key_monitor_window.configure(bg='#2b2b2b')
        
        # Header
        header_frame = tk.Frame(self.key_monitor_window, bg='#2b2b2b')
        header_frame.pack(fill='x', padx=10, pady=10)
        
        title_label = tk.Label(header_frame,
                              text="🔑 Tabla de Llaves - Cliente",
                              font=('Arial', 16, 'bold'),
                              fg='white',
                              bg='#2b2b2b')
        title_label.pack(side='left')
        
        # Información de sincronización
        sync_frame = tk.Frame(self.key_monitor_window, bg='#2b2b2b')
        sync_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.current_key_label = tk.Label(sync_frame,
                                         text=f"Llave Actual: K{self.key_index}",
                                         font=('Arial', 14, 'bold'),
                                         fg='#ffff00',
                                         bg='#2b2b2b')
        self.current_key_label.pack(side='left')
        
        self.psn_label = tk.Label(sync_frame,
                                 text=f"PSN Actual: {self.next_psn}",
                                 font=('Arial', 14, 'bold'),
                                 fg='#0078d4',
                                 bg='#2b2b2b')
        self.psn_label.pack(side='right')
        
        # Frame principal con scroll
        main_frame = tk.Frame(self.key_monitor_window, bg='#2b2b2b')
        main_frame.pack(expand=True, fill='both', padx=10, pady=(0, 10))
        
        # Canvas y scrollbar para la lista de llaves
        canvas = tk.Canvas(main_frame, bg='#1e1e1e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1e1e1e')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Lista de llaves
        self.key_labels = []
        for i, key in enumerate(self.key_table):
            key_frame = tk.Frame(scrollable_frame, bg='#3c3c3c', relief='raised', bd=1)
            key_frame.pack(fill='x', padx=5, pady=2)
            
            # Nombre de la llave
            key_name = tk.Label(key_frame,
                               text=f"K{i:02d}",
                               font=('Consolas', 13, 'bold'),
                               fg='#ffffff',
                               bg='#3c3c3c',
                               width=5)
            key_name.pack(side='left', padx=10, pady=5)
            
            # Hash visual (primeros 8 caracteres del hash de la llave)
            key_hash = hex(hash(key) & 0xFFFFFFFF)[2:].upper().zfill(8)
            hash_label = tk.Label(key_frame,
                                 text=f"Hash: {key_hash}",
                                 font=('Consolas', 12, 'bold'),
                                 fg='#ffffff',
                                 bg='#3c3c3c')
            hash_label.pack(side='left', padx=20)
            
            # Estado de la llave
            status_color = '#ffb900' if i == self.key_index else '#107c10'
            status_text = '🎯 ACTUAL' if i == self.key_index else '🔑 Disponible'
            if i < self.key_index:
                status_text = '✅ Usada'
                status_color = '#888888'
            
            status_label = tk.Label(key_frame,
                                   text=status_text,
                                   font=('Arial', 12, 'bold'),
                                   fg=status_color,
                                   bg='#3c3c3c')
            status_label.pack(side='right', padx=10, pady=5)
            
            self.key_labels.append((key_frame, key_name, hash_label, status_label))
        
        # Botón de actualizar
        refresh_button = tk.Button(self.key_monitor_window,
                                  text="🔄 Actualizar",
                                  font=('Arial', 12, 'bold'),
                                  fg='#ffffff',
                                  bg='#0078d4',
                                  command=self.refresh_key_monitor)
        refresh_button.pack(pady=10)
        
        # Actualizar automáticamente cada segundo
        self.update_key_monitor()
    
    def refresh_key_monitor(self):
        """Actualizar manualmente el monitor de llaves"""
        self.update_key_monitor()
    
    def update_key_monitor(self):
        """Actualizar el estado del monitor de llaves"""
        if self.key_monitor_window is None or not self.key_monitor_window.winfo_exists():
            return
        
        try:
            # Actualizar información de sincronización
            self.current_key_label.config(text=f"Llave Actual: K{self.key_index}")
            self.psn_label.config(text=f"PSN Actual: {self.next_psn}")
            
            # Actualizar estado de cada llave
            for i, (frame, name, hash_label, status_label) in enumerate(self.key_labels):
                if i == self.key_index:
                    status_text = '🎯 ACTUAL'
                    status_color = '#ffb900'
                    frame.config(bg='#4a4a00')  # Resaltar llave actual
                elif i < self.key_index:
                    status_text = '✅ Usada'
                    status_color = '#888888'
                    frame.config(bg='#3c3c3c')
                else:
                    status_text = '🔑 Disponible'
                    status_color = '#107c10'
                    frame.config(bg='#3c3c3c')
                
                status_label.config(text=status_text, fg=status_color)
            
            # Programar próxima actualización
            self.key_monitor_window.after(1000, self.update_key_monitor)
            
        except Exception as e:
            # Si hay error, probablemente la ventana se cerró
            pass
    
    def on_closing(self):
        """Manejar el cierre de la ventana"""
        if self.key_monitor_window is not None and self.key_monitor_window.winfo_exists():
            self.key_monitor_window.destroy()
        if self.connected:
            self.disconnect_from_server()
        self.root.destroy()
    
    def run(self):
        """Ejecutar la aplicación"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.disconnect_from_server()

if __name__ == "__main__":
    client = CryptographyClient()
    client.run()
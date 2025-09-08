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

class CryptographyServer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cryptography Server")
        self.root.geometry("700x600")
        self.root.configure(bg='#2b2b2b')
        self.root.resizable(True, True)
        
        # Configuración de estilo
        self.setup_styles()
        
        # Variables
        self.server_socket = None
        self.clients = []  # Lista de conexiones de clientes
        self.client_states = {}  # Almacenar estado por cliente (address -> (next_psn, next_instruction, key_table, key_index))
        self.running = False
        self.host = '127.0.0.1'
        self.port = 65432
        
        # Generar parámetros del servidor
        self.node_id = generate_node_id(tag="server")
        self.Q = generate_prime(tag="server")  # Primo del servidor
        self.S_server = generate_seed(tag="server")  # Semilla del servidor
        
        # Variables para monitoreo visual
        self.key_monitor_window = None
        self.selected_client = None
        
        # Crear la interfaz del servidor
        self.create_server_interface()
        
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
        
        self.style.configure('Start.TButton',
                           font=('Arial', 12, 'bold'),
                           foreground='white',
                           background='#107c10',
                           borderwidth=0,
                           focuscolor='none')
        
        self.style.map('Start.TButton',
                      background=[('active', '#0e6e0e')])
        
        self.style.configure('Stop.TButton',
                           font=('Arial', 12, 'bold'),
                           foreground='white',
                           background='#d13438',
                           borderwidth=0,
                           focuscolor='none')
        
        self.style.map('Stop.TButton',
                      background=[('active', '#b52529')])
        
        self.style.configure('Send.TButton',
                           font=('Arial', 10, 'bold'),
                           foreground='white',
                           background='#0078d4',
                           borderwidth=0,
                           focuscolor='none')
        
        self.style.map('Send.TButton',
                      background=[('active', '#106ebe')])
    
    def create_server_interface(self):
        """Crear la interfaz del servidor"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#2b2b2b')
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Título
        title_label = ttk.Label(header_frame,
                               text="🔐 Cryptography Server",
                               style='Title.TLabel')
        title_label.pack(side='left')
        
        # Estado del servidor
        self.status_label = ttk.Label(header_frame,
                                    text="● Detenido",
                                    font=('Arial', 12, 'bold'),
                                    foreground='#d13438',
                                    background='#2b2b2b')
        self.status_label.pack(side='right')
        
        # Frame de control
        control_frame = tk.Frame(main_frame, bg='#2b2b2b')
        control_frame.pack(fill='x', pady=(0, 10))
        
        # Información del servidor
        info_label = ttk.Label(control_frame,
                             text=f"Dirección: {self.host}:{self.port}",
                             font=('Arial', 10),
                             foreground='#cccccc',
                             background='#2b2b2b')
        info_label.pack(side='left')
        
        # Botones de control
        button_frame = tk.Frame(control_frame, bg='#2b2b2b')
        button_frame.pack(side='right')
        
        self.start_button = ttk.Button(button_frame,
                                     text="Iniciar Servidor",
                                     style='Start.TButton',
                                     command=self.start_server)
        self.start_button.pack(side='left', padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame,
                                    text="Detener Servidor",
                                    style='Stop.TButton',
                                    command=self.stop_server,
                                    state='disabled')
        self.stop_button.pack(side='left', padx=(0, 10))
        
        # Botón de monitoreo de llaves
        self.monitor_button = ttk.Button(button_frame,
                                       text="Monitor Llaves",
                                       style='Start.TButton',
                                       command=self.show_key_monitor,
                                       state='disabled')
        self.monitor_button.pack(side='left')
        
        # Información de conexiones
        connections_frame = tk.Frame(main_frame, bg='#2b2b2b')
        connections_frame.pack(fill='x', pady=(0, 10))
        
        connections_label = ttk.Label(connections_frame,
                                    text="Conexiones activas:",
                                    font=('Arial', 11, 'bold'),
                                    foreground='white',
                                    background='#2b2b2b')
        connections_label.pack(side='left')
        
        self.connections_count_label = ttk.Label(connections_frame,
                                               text="0",
                                               font=('Arial', 11, 'bold'),
                                               foreground='#ffb900',
                                               background='#2b2b2b')
        self.connections_count_label.pack(side='left', padx=(5, 0))
        
        # Área de log
        log_frame = tk.Frame(main_frame, bg='#2b2b2b')
        log_frame.pack(expand=True, fill='both', pady=(0, 10))
        
        log_label = ttk.Label(log_frame,
                            text="Log del servidor:",
                            font=('Arial', 11, 'bold'),
                            foreground='white',
                            background='#2b2b2b')
        log_label.pack(anchor='w')
        
        self.log_area = scrolledtext.ScrolledText(log_frame,
                                                width=80,
                                                height=15,
                                                bg='#1e1e1e',
                                                fg='white',
                                                font=('Consolas', 9),
                                                state='disabled',
                                                wrap='word')
        self.log_area.pack(expand=True, fill='both', pady=(5, 0))
        
        # Frame para broadcast
        broadcast_frame = tk.Frame(main_frame, bg='#2b2b2b')
        broadcast_frame.pack(fill='x')
        
        broadcast_label = ttk.Label(broadcast_frame,
                                  text="Mensaje broadcast:",
                                  font=('Arial', 10),
                                  foreground='white',
                                  background='#2b2b2b')
        broadcast_label.pack(anchor='w')
        
        input_frame = tk.Frame(broadcast_frame, bg='#2b2b2b')
        input_frame.pack(fill='x', pady=(5, 0))
        
        self.broadcast_entry = tk.Entry(input_frame,
                                      font=('Arial', 11),
                                      bg='#3c3c3c',
                                      fg='white',
                                      insertbackground='white',
                                      border=1,
                                      relief='solid')
        self.broadcast_entry.pack(side='left', expand=True, fill='x', padx=(0, 10))
        self.broadcast_entry.bind('<Return>', self.send_broadcast)
        
        self.send_button = ttk.Button(input_frame,
                                    text="Enviar a todos",
                                    style='Send.TButton',
                                    command=self.send_broadcast,
                                    state='disabled')
        self.send_button.pack(side='right')
        
        # Agregar mensaje de bienvenida
        self.add_log("Sistema", "Servidor inicializado. Presiona 'Iniciar Servidor' para comenzar.", "#ffb900")
    
    def add_log(self, sender, message, color="#ffffff"):
        """Agregar un mensaje al log del servidor"""
        self.log_area.config(state='normal')
        
        # Agregar timestamp
        timestamp = time.strftime("%H:%M:%S")
        
        # Agregar el mensaje
        self.log_area.insert(tk.END, f"[{timestamp}] {sender}: {message}\n")
        
        # Configurar color si es necesario
        if color != "#ffffff":
            start_index = self.log_area.index("end-2l linestart")
            end_index = self.log_area.index("end-1l")
            self.log_area.tag_add("colored", start_index, end_index)
            self.log_area.tag_config("colored", foreground=color)
        
        self.log_area.config(state='disabled')
        self.log_area.see(tk.END)
    
    def start_server(self):
        """Iniciar el servidor"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            
            # Actualizar interfaz
            self.status_label.config(text="● Ejecutándose", foreground="#107c10")
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.monitor_button.config(state='normal')
            self.send_button.config(state='normal')
            
            self.add_log("Servidor", f"Servidor iniciado en {self.host}:{self.port}", "#107c10")
            
            # Iniciar hilo para aceptar conexiones
            accept_thread = threading.Thread(target=self.accept_connections, daemon=True)
            accept_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar el servidor:\n{str(e)}")
            self.add_log("Error", f"No se pudo iniciar el servidor: {str(e)}", "#d13438")
    
    def stop_server(self):
        """Detener el servidor"""
        self.running = False
        
        # Cerrar todas las conexiones de clientes
        for client_socket, client_address in self.clients[:]:
            try:
                client_socket.close()
            except:
                pass
        self.clients.clear()
        self.client_states.clear()
        
        # Cerrar socket del servidor
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        # Actualizar interfaz
        self.status_label.config(text="● Detenido", foreground="#d13438")
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.monitor_button.config(state='disabled')
        self.send_button.config(state='disabled')
        self.update_connections_count()
        
        self.add_log("Servidor", "Servidor detenido", "#d13438")
    
    def accept_connections(self):
        """Aceptar conexiones de clientes en un hilo separado"""
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.clients.append((client_socket, client_address))
                
                # Iniciar hilo para manejar este cliente
                client_thread = threading.Thread(target=self.handle_client, 
                                               args=(client_socket, client_address), 
                                               daemon=True)
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    error_msg = f"Error aceptando conexión: {str(e)}"
                    self.root.after(0, lambda msg=error_msg: self.add_log("Error", msg, "#d13438"))
                break
    
    def handle_client(self, client_socket, client_address):
        """Manejar la comunicación con un cliente específico"""
        try:
            # Mostrar mensaje FCM
            fcm_msg = format_message_log(MessageType.FCM, f"Recibiendo parámetros de {client_address[0]}")
            self.root.after(0, lambda msg=fcm_msg: self.add_log("Sistema", msg, get_message_info(MessageType.FCM)["color"]))
            
            # Recibir parámetros del cliente
            params_data = client_socket.recv(1024).decode()
            P_client, S_client = map(int, params_data.split(','))
            
            # Calcular semilla compartida
            S_shared = self.S_server ^ S_client
            
            # Crear parámetros compartidos
            shared_params = SharedParams(
                id=self.node_id,
                P=P_client,
                Q=self.Q,
                S=S_shared
            )
            
            # Generar tabla de claves
            key_table = generate_key_table(shared_params)
            
            # Almacenar estado del cliente
            self.client_states[client_address] = {
                'next_psn': 0,
                'next_instruction': None,
                'key_table': key_table,
                'key_index': 0,
                'key_regeneration_count': 0
            }
            
            # Enviar parámetros del servidor al cliente
            server_params = f"{self.Q},{self.S_server}"
            client_socket.sendall(server_params.encode())
            
            # Confirmar FCM completado
            fcm_complete = format_message_log(MessageType.FCM, f"Handshake completado con {client_address[0]}")
            self.root.after(0, lambda msg=fcm_complete: self.add_log("Sistema", msg, get_message_info(MessageType.FCM)["color"]))
            
            while self.running:
                data = client_socket.recv(2048)
                if not data:
                    break
                
                try:
                    # Verificar si es un mensaje en texto claro
                    if data.startswith(b"[PLAINTEXT]"):
                        message = data.decode()[11:]  # Remover prefijo [PLAINTEXT]
                        response = "Mensaje en texto claro recibido correctamente"
                        self.root.after(0, lambda msg=message: self.add_log(f"Cliente {client_address[0]} 🔓", f"Dice: {msg}", "#ff9900"))
                        
                        # Enviar respuesta en texto claro
                        plaintext_response = f"[PLAINTEXT]{response}"
                        client_socket.sendall(plaintext_response.encode())
                        continue
                    
                    # Mensaje cifrado - procesar normalmente
                    client_state = self.client_states[client_address]
                    key_index = client_state['key_index']
                    key = client_state['key_table'][key_index]
                    
                    # Verificar si necesitamos regenerar llaves
                    if key_index == 0 and client_state.get('key_regeneration_count', 0) > 0:
                        kum_msg = format_message_log(MessageType.KUM, f"Cliente {client_address[0]} regeneró tabla de llaves (ciclo #{client_state['key_regeneration_count'] + 1})")
                        self.root.after(0, lambda msg=kum_msg: self.add_log("Sistema", msg, get_message_info(MessageType.KUM)["color"]))
                    
                    # Mostrar mensaje RM
                    rm_msg = format_message_log(MessageType.RM, f"Cliente {client_address[0]} - Llave K{key_index:02d}, PSN={client_state['next_psn']}")
                    self.root.after(0, lambda msg=rm_msg: self.add_log("Sistema", msg, get_message_info(MessageType.RM)["color"]))
                    
                    # Desencriptar mensaje
                    result = decrypt_message(data, key.to_bytes(8, 'big'))
                    plaintext = result["plaintext"]
                    message = plaintext.decode()
                    
                    # Debug: mostrar estado antes de actualizar
                    old_psn = client_state['next_psn']
                    debug_msg = f"Servidor antes: PSN={old_psn}, Key=K{key_index}, Mensaje='{message}'"
                    self.root.after(0, lambda msg=debug_msg: self.add_log("Debug", msg, "#888888"))
                    
                    # Actualizar estado del cliente
                    current_instruction = result["next_extraction_instruction"]
                    next_psn = extract_psn_from_plaintext_using_instruction(plaintext, current_instruction)
                    client_state['next_psn'] = next_psn
                    client_state['next_instruction'] = current_instruction
                    old_key_index = key_index
                    client_state['key_index'] = (key_index + 1) % len(client_state['key_table'])
                    
                    # Debug: mostrar estado después de actualizar
                    debug_msg2 = f"Servidor después: PSN {old_psn}→{next_psn}, Key K{old_key_index}→K{client_state['key_index']}"
                    self.root.after(0, lambda msg=debug_msg2: self.add_log("Debug", msg, "#888888"))
                    
                    # Si volvemos al inicio, incrementar contador de regeneración
                    if old_key_index == len(client_state['key_table']) - 1:
                        client_state['key_regeneration_count'] = client_state.get('key_regeneration_count', 0) + 1
                    
                    # Manejar mensajes especiales
                    if message == "First Message Contact":
                        response = "Conexión establecida correctamente"
                        self.root.after(0, lambda: self.add_log(f"Cliente {client_address[0]} 🔐", "Mensaje de contacto inicial recibido", "#0078d4"))
                    elif message == "Last Message Contact":
                        # Mostrar mensaje LCM
                        lcm_msg = format_message_log(MessageType.LCM, f"Cliente {client_address[0]} cerrando conexión")
                        self.root.after(0, lambda msg=lcm_msg: self.add_log("Sistema", msg, get_message_info(MessageType.LCM)["color"]))
                        
                        response = "Desconexión confirmada"
                        # Enviar respuesta encriptada
                        cipher_response = encrypt_message(response.encode(), client_state['next_psn'], key.to_bytes(8, 'big'))
                        client_socket.sendall(cipher_response)
                        
                        # Eliminar estado del cliente (LCM completado)
                        if client_address in self.client_states:
                            del self.client_states[client_address]
                        
                        lcm_complete = format_message_log(MessageType.LCM, f"Tabla de llaves de {client_address[0]} eliminada")
                        self.root.after(0, lambda msg=lcm_complete: self.add_log("Sistema", msg, get_message_info(MessageType.LCM)["color"]))
                        break
                    else:
                        response = "Mensaje cifrado recibido correctamente"
                        self.root.after(0, lambda msg=message: self.add_log(f"Cliente {client_address[0]} 🔐", f"Dice: {msg}", "#ffffff"))
                    
                    # Enviar respuesta encriptada
                    cipher_response = encrypt_message(response.encode(), client_state['next_psn'], key.to_bytes(8, 'big'))
                    client_socket.sendall(cipher_response)
                    
                except Exception as e:
                    error_msg = f"Error procesando mensaje de {client_address[0]}: {str(e)}"
                    self.root.after(0, lambda msg=error_msg: self.add_log("Error", msg, "#d13438"))
                    try:
                        error_response = "Error procesando mensaje"
                        client_socket.sendall(error_response.encode())
                    except:
                        pass
                
        except Exception as e:
            if self.running:
                error_msg = f"Error con cliente {client_address[0]}: {str(e)}"
                self.root.after(0, lambda msg=error_msg: self.add_log("Error", msg, "#d13438"))
        finally:
            # Remover cliente de la lista
            try:
                self.clients.remove((client_socket, client_address))
                if client_address in self.client_states:
                    del self.client_states[client_address]
                client_socket.close()
                self.root.after(0, lambda: self.add_log("Desconexión", f"Cliente {client_address[0]}:{client_address[1]} desconectado", "#ffb900"))
                self.root.after(0, self.update_connections_count)
            except:
                pass
    
    def update_connections_count(self):
        """Actualizar el contador de conexiones"""
        count = len(self.clients)
        self.connections_count_label.config(text=str(count))
    
    def send_broadcast(self, event=None):
        """Enviar mensaje broadcast a todos los clientes conectados"""
        message = self.broadcast_entry.get().strip()
        if not message or not self.clients:
            return
        
        disconnected_clients = []
        sent_count = 0
        
        for client_socket, client_address in self.clients:
            try:
                # Enviar mensaje en texto plano (no encriptado para broadcast)
                client_socket.sendall(f"[BROADCAST] {message}".encode())
                sent_count += 1
            except:
                disconnected_clients.append((client_socket, client_address))
        
        # Remover clientes desconectados
        for client in disconnected_clients:
            try:
                self.clients.remove(client)
                if client[1] in self.client_states:
                    del self.client_states[client[1]]
            except:
                pass
        
        self.add_log("Broadcast", f"Mensaje enviado a {sent_count} cliente(s): {message}", "#ffb900")
        self.broadcast_entry.delete(0, tk.END)
        self.update_connections_count()
    
    def show_key_monitor(self):
        """Mostrar ventana de monitoreo de llaves"""
        if not self.client_states:
            messagebox.showinfo("Monitor de Llaves", "No hay clientes conectados para monitorear.")
            return
            
        if self.key_monitor_window is not None and self.key_monitor_window.winfo_exists():
            self.key_monitor_window.lift()
            return
        
        self.key_monitor_window = tk.Toplevel(self.root)
        self.key_monitor_window.title("🔑 Monitor de Llaves - Servidor")
        self.key_monitor_window.geometry("700x600")
        self.key_monitor_window.configure(bg='#2b2b2b')
        
        # Header
        header_frame = tk.Frame(self.key_monitor_window, bg='#2b2b2b')
        header_frame.pack(fill='x', padx=10, pady=10)
        
        title_label = tk.Label(header_frame,
                              text="🔑 Monitor de Llaves - Servidor",
                              font=('Arial', 16, 'bold'),
                              fg='white',
                              bg='#2b2b2b')
        title_label.pack(side='left')
        
        # Selector de cliente
        client_frame = tk.Frame(self.key_monitor_window, bg='#2b2b2b')
        client_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        tk.Label(client_frame,
                text="Cliente:",
                font=('Arial', 12, 'bold'),
                fg='white',
                bg='#2b2b2b').pack(side='left')
        
        self.client_var = tk.StringVar()
        client_addresses = [f"{addr[0]}:{addr[1]}" for addr in self.client_states.keys()]
        if client_addresses:
            self.client_var.set(client_addresses[0])
            self.selected_client = list(self.client_states.keys())[0]
        
        client_combo = ttk.Combobox(client_frame,
                                   textvariable=self.client_var,
                                   values=client_addresses,
                                   state='readonly',
                                   width=20)
        client_combo.pack(side='left', padx=(10, 0))
        client_combo.bind('<<ComboboxSelected>>', self.on_client_selected)
        
        # Información de sincronización
        self.sync_frame = tk.Frame(self.key_monitor_window, bg='#2b2b2b')
        self.sync_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.current_key_label = tk.Label(self.sync_frame,
                                         text="Llave Actual: K0",
                                         font=('Arial', 12, 'bold'),
                                         fg='#ffb900',
                                         bg='#2b2b2b')
        self.current_key_label.pack(side='left')
        
        self.psn_label = tk.Label(self.sync_frame,
                                 text="PSN Actual: 0",
                                 font=('Arial', 12, 'bold'),
                                 fg='#0078d4',
                                 bg='#2b2b2b')
        self.psn_label.pack(side='right')
        
        # Frame principal con scroll
        main_frame = tk.Frame(self.key_monitor_window, bg='#2b2b2b')
        main_frame.pack(expand=True, fill='both', padx=10, pady=(0, 10))
        
        # Canvas y scrollbar para la lista de llaves
        self.canvas = tk.Canvas(main_frame, bg='#1e1e1e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#1e1e1e')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botón de actualizar
        refresh_button = tk.Button(self.key_monitor_window,
                                  text="🔄 Actualizar",
                                  font=('Arial', 10, 'bold'),
                                  fg='white',
                                  bg='#0078d4',
                                  command=self.refresh_server_key_monitor)
        refresh_button.pack(pady=10)
        
        # Cargar datos iniciales
        self.refresh_server_key_monitor()
        
        # Actualizar automáticamente cada segundo
        self.update_server_key_monitor()
    
    def on_client_selected(self, event):
        """Manejar selección de cliente"""
        selected_text = self.client_var.get()
        if selected_text:
            ip, port = selected_text.split(':')
            self.selected_client = (ip, int(port))
            self.refresh_server_key_monitor()
    
    def refresh_server_key_monitor(self):
        """Actualizar manualmente el monitor de llaves del servidor"""
        if not self.selected_client or self.selected_client not in self.client_states:
            return
        
        # Limpiar frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        client_state = self.client_states[self.selected_client]
        key_table = client_state['key_table']
        key_index = client_state['key_index']
        next_psn = client_state['next_psn']
        
        # Actualizar información de sincronización
        self.current_key_label.config(text=f"Llave Actual: K{key_index}")
        self.psn_label.config(text=f"PSN Actual: {next_psn}")
        
        # Lista de llaves
        self.key_labels = []
        for i, key in enumerate(key_table):
            key_frame = tk.Frame(self.scrollable_frame, bg='#3c3c3c', relief='raised', bd=1)
            key_frame.pack(fill='x', padx=5, pady=2)
            
            # Nombre de la llave
            key_name = tk.Label(key_frame,
                               text=f"K{i:02d}",
                               font=('Consolas', 11, 'bold'),
                               fg='white',
                               bg='#3c3c3c',
                               width=5)
            key_name.pack(side='left', padx=10, pady=5)
            
            # Hash visual (primeros 8 caracteres del hash de la llave)
            key_hash = hex(hash(key) & 0xFFFFFFFF)[2:].upper().zfill(8)
            hash_label = tk.Label(key_frame,
                                 text=f"Hash: {key_hash}",
                                 font=('Consolas', 10),
                                 fg='#cccccc',
                                 bg='#3c3c3c')
            hash_label.pack(side='left', padx=20)
            
            # Estado de la llave
            if i == key_index:
                status_text = '🎯 ACTUAL'
                status_color = '#ffb900'
                key_frame.config(bg='#4a4a00')  # Resaltar llave actual
            elif i < key_index:
                status_text = '✅ Usada'
                status_color = '#888888'
            else:
                status_text = '🔑 Disponible'
                status_color = '#107c10'
            
            status_label = tk.Label(key_frame,
                                   text=status_text,
                                   font=('Arial', 10, 'bold'),
                                   fg=status_color,
                                   bg=key_frame.cget('bg'))
            status_label.pack(side='right', padx=10, pady=5)
            
            self.key_labels.append((key_frame, key_name, hash_label, status_label))
    
    def update_server_key_monitor(self):
        """Actualizar automáticamente el estado del monitor de llaves del servidor"""
        if self.key_monitor_window is None or not self.key_monitor_window.winfo_exists():
            return
        
        try:
            # Actualizar lista de clientes en el combobox
            client_addresses = [f"{addr[0]}:{addr[1]}" for addr in self.client_states.keys()]
            if hasattr(self, 'client_var'):
                current_values = self.key_monitor_window.nametowidget('.!toplevel.!frame2.!combobox')['values']
                if tuple(client_addresses) != current_values:
                    self.key_monitor_window.nametowidget('.!toplevel.!frame2.!combobox')['values'] = client_addresses
            
            # Actualizar datos del cliente seleccionado
            if self.selected_client and self.selected_client in self.client_states:
                self.refresh_server_key_monitor()
            
            # Programar próxima actualización
            self.key_monitor_window.after(1000, self.update_server_key_monitor)
            
        except Exception as e:
            # Si hay error, probablemente la ventana se cerró
            pass
    
    def on_closing(self):
        """Manejar el cierre de la ventana"""
        if self.key_monitor_window is not None and self.key_monitor_window.winfo_exists():
            self.key_monitor_window.destroy()
        if self.running:
            self.stop_server()
        self.root.destroy()
    
    def run(self):
        """Ejecutar la aplicación del servidor"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()

if __name__ == "__main__":
    server = CryptographyServer()
    server.run()
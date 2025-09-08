import socket
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from PSN import encrypt_message, decrypt_message, extract_psn_from_plaintext_using_instruction
from SeedAndPrimes import generate_prime, generate_seed, generate_node_id
from KeyGenerator import generate_key_table
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
        self.stop_button.pack(side='left')
        
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
                    self.root.after(0, lambda: self.add_log("Error", f"Error aceptando conexión: {str(e)}", "#d13438"))
                break
    
    def handle_client(self, client_socket, client_address):
        """Manejar la comunicación con un cliente específico"""
        try:
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
                'key_index': 0
            }
            
            # Enviar parámetros del servidor al cliente
            server_params = f"{self.Q},{self.S_server}"
            client_socket.sendall(server_params.encode())
            
            self.root.after(0, lambda: self.add_log("Handshake", f"Parámetros intercambiados con {client_address[0]}", "#0078d4"))
            
            while self.running:
                data = client_socket.recv(2048)
                if not data:
                    break
                
                try:
                    # Obtener clave actual
                    client_state = self.client_states[client_address]
                    key_index = client_state['key_index']
                    key = client_state['key_table'][key_index]
                    
                    # Desencriptar mensaje
                    result = decrypt_message(data, key.to_bytes(8, 'big'))
                    plaintext = result["plaintext"]
                    message = plaintext.decode()
                    
                    # Actualizar estado del cliente
                    current_instruction = result["next_extraction_instruction"]
                    next_psn = extract_psn_from_plaintext_using_instruction(plaintext, current_instruction)
                    client_state['next_psn'] = next_psn
                    client_state['next_instruction'] = current_instruction
                    client_state['key_index'] = (key_index + 1) % len(client_state['key_table'])
                    
                    # Manejar mensajes especiales
                    if message == "First Message Contact":
                        response = "Conexión establecida correctamente"
                        self.root.after(0, lambda: self.add_log(f"Cliente {client_address[0]}", "Mensaje de contacto inicial recibido", "#0078d4"))
                    elif message == "Last Message Contact":
                        response = "Desconexión confirmada"
                        self.root.after(0, lambda: self.add_log(f"Cliente {client_address[0]}", "Mensaje de desconexión recibido", "#ffb900"))
                        # Enviar respuesta encriptada
                        cipher_response = encrypt_message(response.encode(), client_state['next_psn'], key.to_bytes(8, 'big'))
                        client_socket.sendall(cipher_response)
                        break
                    else:
                        response = "Mensaje recibido correctamente"
                        self.root.after(0, lambda msg=message: self.add_log(f"Cliente {client_address[0]}", f"Dice: {msg}", "#ffffff"))
                    
                    # Enviar respuesta encriptada
                    cipher_response = encrypt_message(response.encode(), client_state['next_psn'], key.to_bytes(8, 'big'))
                    client_socket.sendall(cipher_response)
                    
                except Exception as e:
                    self.root.after(0, lambda: self.add_log("Error", f"Error procesando mensaje de {client_address[0]}: {str(e)}", "#d13438"))
                    try:
                        error_response = "Error procesando mensaje"
                        client_socket.sendall(error_response.encode())
                    except:
                        pass
                
        except Exception as e:
            if self.running:
                self.root.after(0, lambda: self.add_log("Error", f"Error con cliente {client_address[0]}: {str(e)}", "#d13438"))
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
    
    def on_closing(self):
        """Manejar el cierre de la ventana"""
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
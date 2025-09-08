import socket
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time

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
        
        # Crear la interfaz inicial
        self.create_initial_interface()
        
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
            
            # Enviar mensaje inicial
            initial_message = "First Message Contact"
            self.client_socket.sendall(initial_message.encode())
            
            # Cambiar a la interfaz de chat
            self.create_chat_interface()
            
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
                             font=('Arial', 14, 'bold'),
                             foreground='white',
                             background='#2b2b2b')
        chat_title.pack(side='left')
        
        # Estado de conexión
        self.status_label = ttk.Label(header_frame,
                                    text="● Conectado",
                                    font=('Arial', 9),
                                    foreground='#107c10',
                                    background='#2b2b2b')
        self.status_label.pack(side='left', padx=(10, 0))
        
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
                                                  fg='white',
                                                  font=('Consolas', 10),
                                                  state='disabled',
                                                  wrap='word')
        self.chat_area.pack(expand=True, fill='both', pady=(0, 10))
        
        # Frame para entrada de mensaje
        input_frame = tk.Frame(self.chat_frame, bg='#2b2b2b')
        input_frame.pack(fill='x')
        
        # Campo de entrada de mensaje
        self.message_entry = tk.Entry(input_frame,
                                    font=('Arial', 11),
                                    bg='#3c3c3c',
                                    fg='white',
                                    insertbackground='white',
                                    border=1,
                                    relief='solid')
        self.message_entry.pack(side='left', expand=True, fill='x', padx=(0, 10))
        self.message_entry.bind('<Return>', self.send_message)
        
        # Botón de enviar
        send_button = ttk.Button(input_frame,
                               text="Enviar",
                               style='Send.TButton',
                               command=self.send_message)
        send_button.pack(side='right')
        
        # Enfocar el campo de entrada
        self.message_entry.focus()
        
        # Agregar mensaje de bienvenida
        self.add_message_to_chat("Sistema", "Conexión establecida correctamente", "#107c10")
    
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
    
    def send_message(self, event=None):
        """Enviar mensaje al servidor"""
        if not self.connected:
            return
            
        message = self.message_entry.get().strip()
        if not message:
            return
        
        try:
            # Enviar mensaje al servidor
            self.client_socket.sendall(message.encode())
            
            # Agregar mensaje al chat
            self.add_message_to_chat("Tú", message, "#0078d4")
            
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
                response = self.client_socket.recv(1024)
                if response:
                    message = response.decode()
                    # Usar after() para actualizar la GUI desde el hilo principal
                    self.root.after(0, lambda: self.add_message_to_chat("Servidor", message, "#ffb900"))
                else:
                    break
            except Exception as e:
                if self.connected:
                    self.root.after(0, lambda: self.add_message_to_chat("Error", f"Error recibiendo mensaje: {str(e)}", "#d13438"))
                break
    
    def disconnect_from_server(self):
        """Desconectar del servidor"""
        if self.connected:
            try:
                # Enviar mensaje de despedida
                self.client_socket.sendall(b"Last Message Contact")
                
                self.connected = False
                if self.client_socket:
                    self.client_socket.close()
                
                # Actualizar estado
                self.status_label.config(text="● Desconectado", foreground="#d13438")
                self.add_message_to_chat("Sistema", "Conexión cerrada", "#d13438")
                
                # Mostrar mensaje y cerrar después de 2 segundos
                self.root.after(2000, self.root.quit)
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al desconectar: {str(e)}")
    
    def run(self):
        """Ejecutar la aplicación"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.disconnect_from_server()

if __name__ == "__main__":
    client = CryptographyClient()
    client.run()
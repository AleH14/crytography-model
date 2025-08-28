import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = "127.0.0.1"
port = 65432

client_socket.connect((host, port))
client_socket.sendall(b"Hola, servidor, yo soy el cliente")

response = client_socket.recv(1024)
print("Respuesta del servidor:", response.decode())
client_socket.close()
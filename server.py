import socket


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '127.0.0.1'
port = 65432


server_socket.bind((host,port))
server_socket.listen(1)

print(f'server esscuchando en {host}:{port}...')

conn, addr = server_socket.accept()
while True:
    data = conn.recv(1024)
    if not data:
        break
    print("cliente dice: ",data.decode())
    conn.sendall(b"mensaje recido")
conn.close()
server_socket.close()
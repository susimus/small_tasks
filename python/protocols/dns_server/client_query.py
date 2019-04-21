from socket import create_connection as socket_create_connection

SERVER_HOST = '127.0.0.2'
SERVER_PORT = 53

if __name__ == "__main__":
    with socket_create_connection((SERVER_HOST, SERVER_PORT)) as user_socket:
        user_socket.sendall(b'194.226.235.185\r\n')


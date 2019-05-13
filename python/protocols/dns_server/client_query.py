from socket import (
    socket as socket_socket,
    SOCK_STREAM as SOCKET_SOCK_STREAM,
    AF_INET as SOCKET_AF_INET,
    timeout as socket_timeout,
    create_connection as socket_create_connection)

SERVER_HOST = '127.0.0.2'
SERVER_PORT = 53

USER_STOP_COMMAND = "USER_STOP"


if __name__ == "__main__":
    while True:
        console_input = input()
        if console_input == USER_STOP_COMMAND:
            break

        with socket_socket(SOCKET_AF_INET, SOCKET_SOCK_STREAM) as user_socket:
            user_socket.connect((SERVER_HOST, SERVER_PORT))

            user_socket.sendall(console_input.encode())

            print(user_socket.recv(4096).decode())

from socket import (
    socket as socket_socket,
    SOCK_DGRAM as SOCKET_SOCK_DGRAM,
    AF_INET as SOCKET_AF_INET,
    timeout as socket_timeout)

SERVER_HOST = '127.0.0.2'
SERVER_PORT = 53

USER_STOP_COMMAND = "USER_STOP"


if __name__ == "__main__":
    user_socket = socket_socket(SOCKET_AF_INET, SOCKET_SOCK_DGRAM)
    user_socket.settimeout(5)
    while True:
        console_input = input()  # Server can handle only version 4 IP addresses
        if console_input == USER_STOP_COMMAND:
            break

        user_socket.sendto(
            console_input.encode(),
            (SERVER_HOST, 53))
        try:
            print(user_socket.recvfrom(4096)[0].decode())
        except socket_timeout:
            pass

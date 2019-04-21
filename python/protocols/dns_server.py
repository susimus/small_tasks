from time import time
from pickle import (
    dump as pickle_dump,
    load as pickle_load)
from socket import (
    socket,
    AF_INET as SOCKET_AF_INET,
    SOCK_STREAM as SOCKET_SOCK_STREAM,
    SHUT_RDWR as SOCKET_SHUT_RDWR)

SERVER_HOST = '127.0.0.2'
SERVER_PORT = 53
SERVER_CACHE_FILE = "dns_server_cache.dat"

dns_cache = dict()  # { domain1 : {ip1, ip2, ...}, ip3 : {domain2, domain3, ...}, ...}

# Every event_handler cycle check previous seconds if there is removing should be done
last_check_time = time()
expiration_dict = dict()  # { expiration_time : [domain1, ip1, ip2 ...], ... }


def add_to_cache(domain_ip_pair: tuple):
    assert len(domain_ip_pair) == 2
    assert isinstance(domain_ip_pair[0], str) and isinstance(domain_ip_pair[1], str)

    if dns_cache.get(domain_ip_pair[0]) is None:
        dns_cache[domain_ip_pair[0]] = set()
    if dns_cache.get(domain_ip_pair[1]) is None:
        dns_cache[domain_ip_pair[1]] = set()

    dns_cache[domain_ip_pair[0]].add(domain_ip_pair[1])
    dns_cache[domain_ip_pair[1]].add(domain_ip_pair[0])


if __name__ == "__main__":
    try:
        with open(SERVER_CACHE_FILE, "rb") as cache_file:
            dns_cache = pickle_load(cache_file)
            expiration_dict = pickle_load(cache_file)
    except OSError:
        pass

    server_socket = socket(SOCKET_AF_INET, SOCKET_SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(1)
    server_socket.settimeout(5)

    while True:
        user_connection, user_address = server_socket.accept()

        print("Connection from {0}".format(user_address))
        print(user_connection.recv(4096).decode('utf-8'))
        user_connection.shutdown(SOCKET_SHUT_RDWR)
        user_connection.close()
    
    with open(SERVER_CACHE_FILE, "wb") as cache_file:
        pickle_dump(dns_cache, cache_file)
        pickle_dump(expiration_dict, cache_file)

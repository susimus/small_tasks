from time import time
from pickle import (
    dump as pickle_dump,
    load as pickle_load)
from socket import (
    socket,
    AF_INET as SOCKET_AF_INET,
    SOCK_STREAM as SOCKET_SOCK_STREAM,
    SHUT_RDWR as SOCKET_SHUT_RDWR,
    timeout as socket_timeout)
from threading import (
    Thread,
    Lock as threading_Lock)
from os import remove as os_remove


class CachingDNS:
    _SERVER_HOST = '127.0.0.2'
    _SERVER_PORT = 53
    _SERVER_CACHE_FILE = "dns_server_cache.dat"
    _SERVER_STOP_COMMAND = "SERVER_STOP"

    _server_stop_lock = threading_Lock()
    _server_stop_value = False

    _dns_cache = dict()  # { domain1 : {ip1, ip2, ...}, ip3 : {domain2, domain3, ...}, ...}

    # Every event_handler cycle check previous seconds if there is removing should be done
    _last_check_time = time()
    _expiration_dict = dict()  # { expiration_time : [domain1, ip1, ip2 ...], ... }

    def _add_to_cache(self, domain_ip_pair: tuple):
        assert len(domain_ip_pair) == 2
        assert isinstance(domain_ip_pair[0], str) and isinstance(domain_ip_pair[1], str)

        if self._dns_cache.get(domain_ip_pair[0]) is None:
            self._dns_cache[domain_ip_pair[0]] = set()
        if self._dns_cache.get(domain_ip_pair[1]) is None:
            self._dns_cache[domain_ip_pair[1]] = set()

        self._dns_cache[domain_ip_pair[0]].add(domain_ip_pair[1])
        self._dns_cache[domain_ip_pair[1]].add(domain_ip_pair[0])

    def _console_listening(self):
        while True:
            console_input = input('>>')
            if console_input == self._SERVER_STOP_COMMAND:
                with self._server_stop_lock:
                    self._server_stop_value = True
                    break

    def _check_for_expiration(self):  # TODO
        pass

    def main_loop(self):
        self._check_for_expiration()

        try:
            with open(self._SERVER_CACHE_FILE, "rb") as cache_file:
                _dns_cache = pickle_load(cache_file)
                _expiration_dict = pickle_load(cache_file)

            os_remove(self._SERVER_CACHE_FILE)
        except OSError:
            pass

        console_listener = Thread(target=self._console_listening, daemon=True)
        console_listener.start()

        server_socket = socket(SOCKET_AF_INET, SOCKET_SOCK_STREAM)
        server_socket.bind((self._SERVER_HOST, self._SERVER_PORT))
        server_socket.listen(1)
        server_socket.settimeout(1)

        while True:
            try:
                user_connection, user_address = server_socket.accept()
            except socket_timeout:
                with self._server_stop_lock:
                    if self._server_stop_value is True:
                        break

                continue

            assert (user_connection, user_address) != (None, None)

            with user_connection:
                print("Connection from {0}".format(user_address))
                print(user_connection.recv(4096).decode('utf-8'))
                user_connection.shutdown(SOCKET_SHUT_RDWR)

        if len(self._dns_cache) == 0:
            return

        with open(self._SERVER_CACHE_FILE, "wb") as cache_file:
            pickle_dump(self._dns_cache, cache_file)
            pickle_dump(self._expiration_dict, cache_file)


if __name__ == "__main__":
    cachingDNS = CachingDNS()

    cachingDNS.main_loop()

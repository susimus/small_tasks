from time import (
    time as time_time,
    sleep as time_sleep)
from pickle import (
    dump as pickle_dump,
    load as pickle_load)
from typing import Dict, Tuple, Set
from threading import (
    Thread,
    Lock as threading_Lock)
from os import remove as os_remove
# Network modules
from socket import (
    socket as socket_socket,
    AF_INET as SOCKET_AF_INET,
    SOCK_DGRAM as SOCKET_SOCK_DGRAM,
    timeout as socket_timeout)
from dnslib import DNSRecord, DNSError
from urllib.error import URLError


class CachingDNS:
    _SERVER_HOST = '127.0.0.2'
    _SERVER_PORT = 53
    _SERVER_CACHE_FILE = "dns_server_cache.dat"
    _SERVER_STOP_COMMAND = "SERVER_STOP"
    _SERVER_DNS = "10.98.240.10"  # it is router!
    _SERVER_TTL = 100  # seconds

    _server_stop = False

    # Specific thread every event_handler cycle check previous seconds if there is removing should
    # be done
    _cache_lock = threading_Lock()
    _dns_cache: Dict[Tuple[str, str], Set[str]]
    _last_check_time: int
    _expiration_dict: Dict[int, Set[Tuple[str, str, str]]]

    _question_socket = socket_socket(SOCKET_AF_INET, SOCKET_SOCK_DGRAM)
    _question_socket.settimeout(1)

    def _add_to_cache(self, r_name: str, r_type: str, r_data: str) -> None:
        try:
            self._cache_lock.acquire()

            if (r_name, r_type) not in self._dns_cache:
                self._dns_cache[(r_name, r_type)] = {r_data}
            else:
                self._dns_cache[(r_name, r_type)].add(r_data)

            expiration_time = int(time_time()) + self._SERVER_TTL
            if expiration_time in self._expiration_dict:
                self._expiration_dict[expiration_time].add((r_name, r_type, r_data))
            else:
                self._expiration_dict[expiration_time] = {(r_name, r_type, r_data)}
        finally:
            self._cache_lock.release()

    def _console_listening(self) -> None:
        while True:
            console_input = input()
            if console_input == self._SERVER_STOP_COMMAND:
                self._server_stop = True
                break

    def _expiration_checking(self) -> None:
        while True:
            time_sleep(1)

            try:
                self._cache_lock.acquire()

                current_check_time = int(time_time())
                for some_time in range(self._last_check_time, current_check_time):
                    if some_time in self._expiration_dict:
                        for r_name, r_type, r_data in self._expiration_dict.pop(some_time):
                            if (r_name, r_type) in self._dns_cache:
                                self._dns_cache[(r_name, r_type)].remove(r_data)

                                if len(self._dns_cache[(r_name, r_type)]) == 0:
                                    self._dns_cache.pop((r_name, r_type))

                self._last_check_time = current_check_time
            finally:
                self._cache_lock.release()

    def _resolve_question(self, resolve_question: DNSRecord, ns_address: str) -> DNSRecord:
        self._question_socket.sendto(resolve_question.pack(), (ns_address, 53))

        try:
            ns_raw_answer, _ = self._question_socket.recvfrom(4096)

            return DNSRecord.parse(ns_raw_answer)
        except (socket_timeout, DNSError):
            return DNSRecord()

    def main_loop(self) -> None:
        try:
            self._cache_lock.acquire()

            with open(self._SERVER_CACHE_FILE, "rb") as cache_file:
                self._dns_cache = pickle_load(cache_file)
                self._expiration_dict = pickle_load(cache_file)
                self._last_check_time = pickle_load(cache_file)

            os_remove(self._SERVER_CACHE_FILE)
        except OSError:
            self._dns_cache = dict()
            self._expiration_dict = dict()
            self._last_check_time = int(time_time())
        finally:
            self._cache_lock.release()

        console_listener = Thread(target=self._console_listening, daemon=True)
        console_listener.start()

        expiration_checker = Thread(target=self._expiration_checking, daemon=True)
        expiration_checker.start()

        server_socket = socket_socket(SOCKET_AF_INET, SOCKET_SOCK_DGRAM)
        server_socket.bind((self._SERVER_HOST, self._SERVER_PORT))
        server_socket.settimeout(1)

        while True:
            try:
                user_data, user_address = server_socket.recvfrom(4096)
            except socket_timeout:
                if self._server_stop:
                    break

                continue

            assert (user_data, user_address) != (None, None)

            try:
                self._cache_lock.acquire()

                cache_rr = (user_data.decode(), "A")
                if cache_rr in self._dns_cache:
                    print('cache used: ' + str(self._dns_cache[cache_rr]))

                    self._question_socket.sendto(
                        ("Non-Authoritative answer:\n"
                         + str(self._dns_cache[cache_rr])).encode(),
                        user_address)

                    continue
            finally:
                self._cache_lock.release()

            user_question = DNSRecord.question(user_data.decode(), "NS")
            try:
                parsed_answer_ns = self._resolve_question(
                    user_question,
                    self._SERVER_DNS)

                for resource_record_ns in parsed_answer_ns.rr:
                    ns_ip_answer = self._resolve_question(
                        DNSRecord.question(str(resource_record_ns.rdata), "A"),
                        self._SERVER_DNS)
                    if len(ns_ip_answer.rr) == 0:
                        continue

                    resolved_question = self._resolve_question(
                        DNSRecord.question(user_data.decode(), "A"),
                        str(ns_ip_answer.rr[0].rdata))
                    if len(resolved_question.rr) == 0:
                        continue

                    # TODO: Send to user not only first address
                    # TODO: Collect all rrs from final dns
                    self._add_to_cache(
                        user_data.decode(),
                        "A",
                        str(resolved_question.rr[0].rdata))
                    self._question_socket.sendto(
                        ("Non-Authoritative answer:\n"
                         + str(resolved_question.rr[0].rdata)).encode(),
                        user_address)
                else:
                    self._question_socket.sendto(
                        "Cannot resolve query".encode(),
                        user_address)
            except (URLError, socket_timeout, DNSError) as occurred_error:
                self._question_socket.sendto(
                    ("Error occurred while data was resolving:\n"
                     + str(occurred_error)).encode(),
                    user_address)

        if len(self._dns_cache) == 0:
            return

        self._cache_lock.acquire()
        with open(self._SERVER_CACHE_FILE, "wb") as cache_file:
            pickle_dump(self._dns_cache, cache_file)
            pickle_dump(self._expiration_dict, cache_file)
            pickle_dump(self._last_check_time, cache_file)


if __name__ == "__main__":
    cachingDNS = CachingDNS()

    cachingDNS.main_loop()

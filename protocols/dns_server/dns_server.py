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
from re import (
    fullmatch as re_fullmatch,
    compile as re_compile)
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
    _SERVER_TTL = 1000  # seconds

    _IP_REGEXP = re_compile(r'\b((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}\b')
    _QUERY_FORMAT_REGEXP = re_compile(r'(ip|domain)\s(\w+\.)+\w+\s(A|AAAA|PTR|NS)$')

    _server_stop = False

    _cache_lock = threading_Lock()
    _dns_cache: Dict[Tuple[str, str], Set[str]] = dict()
    _expiration_dict: Dict[int, Set[Tuple[str, str, str]]] = dict()
    _last_check_time: int = int(time_time())

    _server_socket = socket_socket(SOCKET_AF_INET, SOCKET_SOCK_DGRAM)
    _server_socket.bind((_SERVER_HOST, _SERVER_PORT))
    _server_socket.settimeout(1)

    _question_socket = socket_socket(SOCKET_AF_INET, SOCKET_SOCK_DGRAM)
    _question_socket.settimeout(1)

    def _add_to_cache(self, r_name: str, r_type: str, r_data: str) -> None:
        with self._cache_lock:
            if (r_name, r_type) not in self._dns_cache:
                self._dns_cache[(r_name, r_type)] = {r_data}
            else:
                self._dns_cache[(r_name, r_type)].add(r_data)

            expiration_time = int(time_time()) + self._SERVER_TTL
            if expiration_time in self._expiration_dict:
                self._expiration_dict[expiration_time].add((r_name, r_type, r_data))
            else:
                self._expiration_dict[expiration_time] = {(r_name, r_type, r_data)}

    def _console_listening(self) -> None:
        while True:
            console_input = input()
            if console_input == self._SERVER_STOP_COMMAND:
                self._server_stop = True
                break

    def _expiration_checking(self) -> None:
        while True:
            time_sleep(1)

            with self._cache_lock:
                current_check_time = int(time_time())
                for some_time in range(self._last_check_time, current_check_time):
                    if some_time in self._expiration_dict:
                        for r_name, r_type, r_data in self._expiration_dict.pop(some_time):
                            if (r_name, r_type) in self._dns_cache:
                                self._dns_cache[(r_name, r_type)].remove(r_data)

                                if len(self._dns_cache[(r_name, r_type)]) == 0:
                                    self._dns_cache.pop((r_name, r_type))

                self._last_check_time = current_check_time

    def _resolve_question(self, resolve_question: DNSRecord, ns_address: str) -> DNSRecord:
        self._question_socket.sendto(resolve_question.pack(), (ns_address, 53))

        try:
            ns_raw_answer, _ = self._question_socket.recvfrom(4096)

            return DNSRecord.parse(ns_raw_answer)
        except (socket_timeout, DNSError):
            return DNSRecord()

    def _init_mainloop(self) -> None:
        try:
            with open(self._SERVER_CACHE_FILE, "rb") as cache_file, self._cache_lock:
                self._dns_cache = pickle_load(cache_file)
                self._expiration_dict = pickle_load(cache_file)
                self._last_check_time = pickle_load(cache_file)

            os_remove(self._SERVER_CACHE_FILE)
        except OSError:
            self._dns_cache = dict()
            self._expiration_dict = dict()
            self._last_check_time = int(time_time())

        console_listener = Thread(target=self._console_listening, daemon=True)
        console_listener.start()

        expiration_checker = Thread(target=self._expiration_checking, daemon=True)
        expiration_checker.start()

    def _create_cache_file(self) -> None:
        with open(self._SERVER_CACHE_FILE, "wb") as cache_file, self._cache_lock:
            pickle_dump(self._dns_cache, cache_file)
            pickle_dump(self._expiration_dict, cache_file)
            pickle_dump(self._last_check_time, cache_file)

    def _collect_all_rrs_from_ns(
            self,
            user_data_address: str,
            user_data_domain: str,
            ns_of_domain: str) -> None:
        # 'A' and "AAAA" questions
        for query_type in ('A', "AAAA"):
            resolved_question = self._resolve_question(
                DNSRecord.question(user_data_domain, query_type),
                ns_of_domain)
            for resource_record in resolved_question.rr:
                self._add_to_cache(
                    user_data_domain,
                    query_type,
                    str(resource_record.rdata))

        # "NS" question
        resolved_question = self._resolve_question(
            DNSRecord.question(user_data_domain, "NS"),
            ns_of_domain)
        for resource_record in resolved_question.rr:
            self._add_to_cache(
                user_data_address,
                "NS",
                str(resource_record.rdata))

        # "PTR" question
        if user_data_address == user_data_domain:
            return

        inverse_domain_from_ip = '.'.join(user_data_address.split('.')[::-1]) + '.in-addr.arpa'
        resolved_question = self._resolve_question(
            DNSRecord.question(inverse_domain_from_ip, "PTR"),
            ns_of_domain)
        for resource_record in resolved_question.rr:
            self._add_to_cache(
                user_data_address,
                "PTR",
                str(resource_record.rdata))

    def main_loop(self) -> None:
        self._init_mainloop()

        while True:
            try:
                user_data, user_ip_address = self._server_socket.recvfrom(4096)
            except socket_timeout:
                if self._server_stop:
                    break

                continue

            user_data_string = user_data.decode()

            if (re_fullmatch(
                    self._QUERY_FORMAT_REGEXP,
                    user_data_string) is None
                    or (user_data_string.startswith('ip') and
                        re_fullmatch(self._IP_REGEXP, user_data_string.split(' ')[1]) is None)):
                self._question_socket.sendto(
                    ("Incorrect question format. "
                     "Format: '(ipv4|domain) address (A|AAAA|PTR|NS)").encode(),
                    user_ip_address)
                continue

            assert len(user_data_string.split(' ')) == 3

            user_data_address_format, user_data_address, user_data_qtype = (
                user_data_string.split(' '))

            cache_rr = (user_data_address, user_data_qtype)
            with self._cache_lock:
                if cache_rr in self._dns_cache:
                    print('cache used: ' + str(self._dns_cache[cache_rr]))

                    self._question_socket.sendto(
                        ("Non-Authoritative answer:\n"
                         + str(self._dns_cache[cache_rr])).encode(),
                        user_ip_address)

                    continue

            try:
                if user_data_address_format == 'domain':
                    user_data_domain = user_data_address
                else:  # if ip
                    inverse_domain_from_ip = ('.'.join(user_data_address.split('.')[::-1]) +
                                              '.in-addr.arpa')
                    domain_question = DNSRecord.question(
                        inverse_domain_from_ip,
                        "PTR")
                    answer_with_domain = self._resolve_question(
                        domain_question,
                        self._SERVER_DNS)

                    if len(answer_with_domain.rr) == 0:
                        self._question_socket.sendto(
                            "Cannot resolve ip. Local DNS can't give domain from ip".encode(),
                            user_ip_address)

                        continue

                    user_data_domain = str(answer_with_domain.rr[0].rdata)

                user_question = DNSRecord.question(user_data_domain, "NS")

                answer_with_ns_names = self._resolve_question(
                    user_question,
                    self._SERVER_DNS)

                for resource_record_from_ns in answer_with_ns_names.rr:
                    answer_with_ns_ips = self._resolve_question(
                        DNSRecord.question(str(resource_record_from_ns.rdata), "A"),
                        self._SERVER_DNS)

                    if len(answer_with_ns_ips.rr) == 0:
                        continue

                    self._collect_all_rrs_from_ns(
                        user_data_address,
                        user_data_domain,
                        str(answer_with_ns_ips.rr[0].rdata))  # Only one ns ip checks

                    with self._cache_lock:
                        if cache_rr in self._dns_cache:
                            self._question_socket.sendto(
                                ("Non-Authoritative answer:\n"
                                 + str(self._dns_cache[cache_rr])).encode(),
                                user_ip_address)
                        else:
                            continue

                    break
                else:
                    self._question_socket.sendto(
                        "Cannot resolve query".encode(),
                        user_ip_address)
            except (URLError, socket_timeout, DNSError) as occurred_error:
                self._question_socket.sendto(
                    ("Error occurred while data was resolving:\n"
                     + str(occurred_error)).encode(),
                    user_ip_address)

        if len(self._dns_cache) == 0:
            return

        self._create_cache_file()


if __name__ == "__main__":
    cachingDNS = CachingDNS()

    cachingDNS.main_loop()

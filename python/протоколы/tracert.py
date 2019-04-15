from subprocess import (
    Popen as subprocess_Popen,
    PIPE as PROCESS_PIPE,
    TimeoutExpired as TimeoutExpiredError)
from argparse import ArgumentParser
from time import time, sleep as time_sleep
from sys import exit as sys_exit
from io import StringIO
from urllib.request import (
    Request as urllib_Request,
    urlopen)
from urllib.error import URLError
from json import loads as json_loads
from re import sub as re_sub

ERR_TRACERT_ERROR = 1
ERR_NODE_NAME_ERROR = 2
ERR_TRANSITION_ERROR = 3
ERR_INTERNET_CONNECTION_ERROR = 4

argParser = ArgumentParser(
    description="Трассировка автономных систем. Пользователь вводит доменное "
                "имя или IP адрес. Осуществляется трассировка до указанного узла. На "
                "выходе таблица со столбцами: номер узла, IP, ASN, страна и провайдер")
argParser.add_argument(
    'internet_address',
    type=str,
    help='IP или доменное имя')
args = argParser.parse_args()

tracert = subprocess_Popen(
    ['tracert', args.internet_address],
    stdout=PROCESS_PIPE,
    stderr=PROCESS_PIPE)

start_time = time()
tracert_out = ""
while True:
    try:
        tracert_stdout, tracert_stderr = tracert.communicate(timeout=10)
        break
    except TimeoutExpiredError:
        print("tracert in progress " + str(int(time() - start_time)) + " seconds...")

tracert_out = StringIO(tracert_stdout.decode('cp866'))
tracert_err = tracert_stderr.decode('cp866')

if tracert_err != "":
    print(tracert_err)
    sys_exit(ERR_TRACERT_ERROR)

tracert_line = tracert_out.readline()
if tracert_line.startswith('Не удается разрешить системное имя узла'):
    print(tracert_line)
    sys_exit(ERR_NODE_NAME_ERROR)

for i in range(2):
    tracert_out.readline()
tracert_line = tracert_out.readline()
if not tracert_line.startswith('  1'):
    tracert_line = tracert_out.readline()

tracert_line = re_sub(' +', ' ', tracert_line)
counter = 1
while len(tracert_line) > 5:
    if 'Ошибка передачи' in tracert_line:
        print('Ошибка передачи')
        sys_exit(ERR_TRANSITION_ERROR)
    if "Превышен интервал ожидания для запроса." in tracert_line:
        print(str(counter) + "\t" + " ".join(tracert_line.split(' ')[5:]))
        break

    node_ip = tracert_line.split(' ')[-2]
    if node_ip.startswith('['):
        node_ip = node_ip[1:-1]

    url_iptoasn = 'https://api.iptoasn.com/v1/as/ip/' + node_ip
    request = urllib_Request(url_iptoasn, headers={'User-Agent': 'Mozilla/5.0'})
    json_answer = {}
    try:
        json_answer = json_loads(urlopen(request).read().decode('utf-8'))
        time_sleep(0.5)
    except URLError as error:
        print("Internet connection problem occurred:")
        print(str(error))
        sys_exit(ERR_INTERNET_CONNECTION_ERROR)

    if counter == 1:
        print('№\tIP\t\tASN\tCOUNTRY\tPROVIDER')

    if 'announced' not in json_answer:
        print(f'{counter}\tIncorrect data in json_answer')
    elif not json_answer['announced']:
        print(f'{counter}\t{node_ip}\tNot announced')
    else:
        as_number = json_answer['as_number']
        as_country_code = json_answer['as_country_code']
        as_description = json_answer['as_description']
        print(
            f'{counter}\t{node_ip}\t'
            f"{as_number}\t{as_country_code}\t{as_description}")

    tracert_line = re_sub(' +', ' ', tracert_out.readline())
    counter += 1

# domains.kaufen
# hello.tokyo
# google.com
# e1.ru 212.193.163.7

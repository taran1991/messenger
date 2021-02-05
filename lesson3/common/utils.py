import sys
import os
import argparse

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from config import DEFAULT_PORT, DEFAULT_HOST


def parce_command_line():
    """Создаём парсер аргументов коммандной строки
    и читаем параметры, возвращаем 3 параметра
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', default=DEFAULT_HOST, nargs='?')
    parser.add_argument('-p', '--port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    host = namespace.addr
    port = namespace.port
    name = namespace.name
    return port, host, name

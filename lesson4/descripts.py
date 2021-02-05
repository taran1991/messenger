import logging
import sys

from subprocess import Popen, PIPE
from ipaddress import ip_address

from common.defines import MIN_PORT, MAX_PORT


class Port(object):
    def __set__(self, instance, port):
        if not MIN_PORT < port < MAX_PORT:
            logging.critical(
                f'Попытка запуска с неподходящим номером порта: {port}. '
                f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
            sys.exit(1)
        instance.__dict__[self.name] = port

    def __set_name__(self, owner, name):
        self.name = name


class Host(object):
    def __set__(self, instance, ip):
        try:
            ipv4 = ip_address(ip)
        except:
            ipv4 = ip

        proc = Popen(f"ping {ipv4} -w 5", shell=True, stdout=PIPE)
        proc.wait()
        if proc.returncode != 0:
            logging.critical(f'хост не доступен {ip}. ')
            sys.exit(1)
        instance.__dict__[self.name] = ip

    def __set_name__(self, owner, name):
        self.name = name

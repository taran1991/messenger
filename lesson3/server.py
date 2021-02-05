"""
Коды ответов сервера
JIM-протокол использует коды ошибок HTTP. Перечислим поддерживаемые:
1xx — информационные сообщения:
100 — базовое уведомление;
101 — важное уведомление.
2xx — успешное завершение:
200 — OK;
201 (created) — объект создан;
202 (accepted) — подтверждение.
4xx — ошибка на стороне клиента:
400 — неправильный запрос/JSON-объект;
401 — не авторизован;
402 — неправильный логин/пароль;
403 (forbidden) — пользователь заблокирован;
404 (not found) — пользователь/чат отсутствует на сервере;
409 (conflict) — уже имеется подключение с указанным логином;
410 (gone) — адресат существует, но недоступен (offline).
5xx — ошибка на стороне сервера:
500 — ошибка сервера.
Коды ответов сервира импортируются из common.config
"""


import json
import select
import threading

from common.utils import parce_command_line
from common.config import SERVER_MESSAGES, MAX_CONNECTIONS, ACTIONS_FLAGS
from connector import Connector
from decos import log_cls
from logs.logs_utils import create_logger
from logs.logs_config import SERVER_CONFIG
from metaclasses import ServerMaker
from server_database import ServerStorage


LOGGER = create_logger(SERVER_CONFIG)


@log_cls
class Server(Connector, metaclass=ServerMaker):

    def connect(self, timeout=None):
        self.socket.bind((self.host, self.port))
        if timeout:
            self.socket.settimeout(timeout)
        self.socket.listen(MAX_CONNECTIONS)
        LOGGER.info(
            f'Запущен сервер, порт для подключений: {self.port}, '
            f'адрес с которого принимаются подключения: {self.host}. '
            f'Если адрес не указан, принимаются соединения с любых адресов.')


    def _get_response_code(self, message):
        if 'action' in message and 'time' in message:
            return 200
        else:
            return 400

    def _get_response_message(self, message_from_cient, time=None):
        response_code = self._get_response_code(message_from_cient)
        if message_from_cient['action'] == 'presence' or response_code == 400:
            message_type = 'alert' if 100 < response_code < 300 else 'error'
            return {
                        "response": response_code,
                        "time": self.get_str_time(time),
                        message_type: SERVER_MESSAGES[response_code]
                       }
        else:
            return {
                'action': 'msg',
                'to': message_from_cient['to'],
                'from': message_from_cient['from'],
                'time': self.get_str_time(time),
                'message': message_from_cient['message']
            }

    def response_to_client(self, time=None):
        client, client_address = self.socket.accept()
        try:
            message_from_cient = self.get_message(client)
            response = self._get_response_message(message_from_cient, time)
            self.send_message(response, client)
            client.close()
        except (ValueError, json.JSONDecodeError):
            client.close()
            LOGGER.error(f'Принято некорретное сообщение от клиента {client}')

    def response_to_clients(self, time=None):
        clients = []

        while True:
            responses = []
            try:
                client, client_address = self.socket.accept()
            except OSError:
                pass
            else:
                LOGGER.info(f'Установлено соедение с ПК {client_address}')
                clients.append(client)


            try:
                clients_to_read, clients_to_answer, err_lst = select.select(clients, clients, [], 0)
            except OSError:
                clients_to_read, clients_to_answer, err_lst = [], [], []

            for client in clients_to_read:
                try:
                    message_from_cient = self.get_message(client)
                    if message_from_cient['action'] == 'presence':
                        self.database.user_login(message_from_cient['from'], client_address[0], client_address[1])
                    response = self._get_response_message(message_from_cient, time)
                    if 'action' in response:
                        responses.append(response)
                    else:
                        self.send_message(response, client)
                except:
                    LOGGER.info(f'Клиент {client.getpeername()} отключился от сервера.')
                    self.database.user_logout(client.getpeername()[0], client.getpeername()[1])
                    clients.remove(client)
            for client in clients_to_answer:
                try:
                    for response in responses:
                        self.send_message(response, client)
                except:
                    LOGGER.info(f'Клиент {client.getpeername()} отключился от сервера.')
                    clients.remove(client)

def print_help():
    print('Поддерживаемые комманды:')
    print('users - список известных пользователей')
    print('connected - список подключенных пользователей')
    print('loghist - история входов пользователя')
    print('exit - завершение работы сервера.')
    print('help - вывод справки по поддерживаемым командам')


def main():
    # server.py -a 192.168.1.2 -p 8079
    database = ServerStorage()
    port, host, user = parce_command_line()
    server = Server(port, host, database)
    # server.daemon = True
    server.connect(timeout=0.5)
    server.response_to_clients()

    # print_help()
    # while True:
    #     command = input('Введите комманду: ')
    #     if command == 'help':
    #         print_help()
    #     elif command == 'exit':
    #         break
    #     elif command == 'users':
    #         for user in sorted(database.users_list()):
    #             print(f'Пользователь {user[0]}, последний вход: {user[1]}')
    #     elif command == 'connected':
    #         for user in sorted(database.active_users_list()):
    #             print(f'Пользователь {user[0]}, подключен: {user[1]}:{user[2]}, время установки соединения: {user[3]}')
    #     elif command == 'loghist':
    #         name = input('Введите имя пользователя для просмотра истории. Для вывода всей истории, просто нажмите Enter: ')
    #         for user in sorted(database.login_history(name)):
    #             print(f'Пользователь: {user[0]} время входа: {user[1]}. Вход с: {user[2]}:{user[3]}')
    #     else:
    #         print('Команда не распознана.')


if __name__ == '__main__':
    main()
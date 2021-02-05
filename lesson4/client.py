import sys
import json
from json import JSONDecodeError
from time import sleep
from threading import Thread

from common.utils import parce_command_line
from common.config import ENCODING, ACTIONS_FLAGS
from connector import Connector
from decos import log_cls
from errors import ServerError, ReqFieldMissingError, IncorrectDataReceivedError
from logs.logs_utils import create_logger
from logs.logs_config import CLIENT_CONFIG
from common.config import ENCODING, DEFAULT_PORT, DEFAULT_HOST
from metaclasses import ClientMaker

LOGGER = create_logger(CLIENT_CONFIG)

@log_cls
class Client(Connector, metaclass=ClientMaker):
    def __init__(self, user, port=DEFAULT_PORT, host=DEFAULT_HOST, encoding=ENCODING):
        self.user = user
        super().__init__(port, host, encoding)

    def connect(self):
        self.socket.connect((self.host, self.port))

    def send_message_from_user(self, message, user_to, encoding=ENCODING, time=None):
        message = {
                   "action": ACTIONS_FLAGS['message'],
                   "time": self.get_str_time(time),
                   "to": user_to,
                   "from": self.user,
                   "encoding": encoding,
                   "message": message
        }
        self.send_message(message)

    def _create_request_for_chart(self, room, action, time=None):
        return {
                    "action": action,
                    "time": self.get_str_time(time),
                    "room": room
                }

    def request_to_join_to_chat(self, room, time=None):
        message = self._create_request_for_chart(room, ACTIONS_FLAGS['join_to_chat'], time)
        self.send_message(message)

    def request_to_leave_chat(self, room, time=None):
        message = self._create_request_for_chart(room, ACTIONS_FLAGS['leave_chat'], time)
        self.send_message(message)
        # CLIENT_LOGGER.debug(f'клиент отправил сообщение {message}')

    def send_presence_message(self, time=None):
        message = {
            "action": ACTIONS_FLAGS['presence'],
            "time": self.get_str_time(time),
            'from': self.user
            }
        self.send_message(message)

    def run_listern_mode(self):
        """Функция обрабатывает сообщения от других пользователей, поступившие с сервера"""
        while True:
            try:
                message = self.get_message()
                if 'action' in message and message['action'] == 'msg' and 'time' in message \
                        and 'from' in message and 'to' in message and 'message' in message:
                    if message['to'] == self.user:
                        print(f'{message["time"]} - {message["to"]}: {message["message"]}')
                        LOGGER.info(f'Пользователь {self.user} получил сообщение {message["message"]}'
                                    f' от пользователя {message["from"]}')
                    else:
                        continue
                elif "response" in message and message["response"] == 400:
                    LOGGER.debug(f'Получен отвен "Response 400: {message["error"]}".')
                    print(f'{message["error"]}')
                else:
                    LOGGER.error(f'Принято некорректное сообщение {message}')
            except IncorrectDataReceivedError:
                LOGGER.error('Не удалось декодировать полученное сообщение')
            except (ConnectionError, ConnectionRefusedError, ConnectionAbortedError, OSError, JSONDecodeError):
                LOGGER.critical(f'Соединение с сервером потеряно')
                break

    def _get_help(self):
        """Функция возвращает справочную информацию"""
        print('Доступные команды:')
        print('1 - отправить сообщение.')
        print('2 - вывести подсказки по командам.')
        print('3 - выйти из программы.')

    def interact_with_user(self):
        """Функция для работы юзера, вызывает пользовательское меню"""
        self._get_help()
        while True:
            command = input('Выберите действие (помощь "2"): ')
            if command == '1':
                recipient = input('Введите имя получателя: ')
                message = input('Введите сообщение: ')
                self.send_message_from_user(message, recipient)
            elif command == '2':
                self._get_help()
            elif command == '3':
                print('Работа программы завершена.')
                LOGGER.info(f'Клиент {self.user} завершил работу.')
                # Задержка неоходима, чтобы успело уйти сообщение о выходе
                sleep(0.5)
                break
            else:
                print('Команда не распознана.')


def main():
    # client.py -a 192.168.1.2 -p 8079 -m send
    port, host, name = parce_command_line()
    if not name:
        name = input('Введите имя пользователя: ')
    LOGGER.info(f'Запущено клиентское приложение. IP-адрес сервера: {host},'
                f' порт сервера: {port}, имя пользователя: {name}.')
    try:
        client = Client(name, port, host)
        client.connect()
        client.send_presence_message()
        answer = client.get_message()
        LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        if answer['response'] >= 400:
            raise ServerError(f'400 : {answer["error"]}')
    except json.JSONDecodeError:
        LOGGER.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ServerError as error:
        LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        pass
    except ReqFieldMissingError as missing_error:
        LOGGER.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        sys.exit(1)
    except ConnectionRefusedError:
        LOGGER.critical(
            f'Не удалось подключиться к серверу {host}:{port}, '
            f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    else:
        # Если соединение с сервером установлено корректно, запускаем процесс приема сообщений
        #Запуск потока на получение сообщения
        receiver = Thread(target=client.run_listern_mode)
        receiver.daemon = True
        receiver.start()
        # Запуск потока на отправление сообщения
        user_interface = Thread(target=client.interact_with_user)
        user_interface.daemon = True
        user_interface.start()

        # Если один из потоков завершён, значит или потеряно соединение или пользователь
        # ввёл exit. Т.к. все события обработываются в потоках, достаточно завершить цикл.
        while True:
            sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()

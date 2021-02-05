import logging
import os

DEFAULT_PORT = 8888
DEFAULT_HOST = '127.0.0.1'
MAX_CONNECTIONS = 5
MAX_PACKAGE_LENGTH = 1024
ENCODING = 'utf-8'


"""
“action”: “presence”: 'presence': присутствие. Сервисное сообщение для извещения сервера о присутствии клиента online,
“action”: “presence_check”: 'prоbe': проверка присутствия. Сервисное сообщение от сервера для проверки присутствии
 клиента online,
“action”: “message”: 'msg': простое сообщение пользователю или в чат,
“action”: “quit_server“: 'quit': отключение от сервера,
“action”: “authenticate”: 'authenticate': авторизация на сервере,
“action”: “join_chat”: 'join': присоединиться к чату,
“action”: “leave_chat”: 'leave': покинуть чат.
"""

ACTIONS_FLAGS = {
    'presence': 'presence',
    'presence_check': 'prоbe',
    'message': 'msg',
    'authenticate': 'authenticate',
    'join_to_chat': 'join',
    'leave_chat': 'leave',
    'quit_server': 'quit'
}

SERVER_MESSAGES = {
    100: 'базовое уведомление',
    101:  'важное уведомление',
    200: 'OK',
    201: 'объект создан',
    202: 'подтверждение',
    400: 'неправильный запрос/JSON-объект',
    401: 'не авторизован',
    402: 'неправильный логин/пароль',
    403: 'пользователь заблокирован',
    404: 'пользователь/чат отсутствует на сервере',
    409: 'уже имеется подключение с указанным логином',
    410: 'адресат существует, но недоступен (offline)',
    500: 'ошибка сервера',
}

SERVER_DATABASE = 'sqlite:///server_base.db3'
POOL_RECYCLE = 7200 #8 часов
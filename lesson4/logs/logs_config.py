import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from logs_utils import test_logger

CLIENT_CONFIG = {
    'format': '%(asctime)s %(levelname)s %(filename)s %(message)s',
    'stream_handler': sys.stderr,
    'stream_handler_error': logging.ERROR,
    'logs_path': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_logs', 'logs.log'),
    'encoding': 'utf-8',
    'timed_rotating': False,
    'logging_level': logging.DEBUG,
    'app_name': 'server'
}

SERVER_CONFIG = {
    'format': '%(asctime)s %(levelname)s %(filename)s %(message)s',
    'stream_handler': sys.stderr,
    'stream_handler_error': logging.ERROR,
    'logs_path': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server_logs', 'logs.log'),
    'encoding': 'utf-8',
    'timed_rotating': True,
    'time_interval': 1,
    'interval_type': 'D',
    'logging_level': logging.DEBUG,
    'app_name': 'server'
}

"""Проверка логов"""
if __name__ == '__main__':
    test_logger(CLIENT_CONFIG)
    test_logger(SERVER_CONFIG)

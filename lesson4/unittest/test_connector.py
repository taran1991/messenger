import sys
import os
import unittest


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


from common.config import ACTIONS_FLAGS
from connector import Connector
from socket_simulation import TestSocket


class Tests(unittest.TestCase):
    test_dict_send = {
        'action': ACTIONS_FLAGS['presence'],
        'time': 111111.111111,
        'user': {
            'account_name': 'test_test'
        }
    }
    test_dict_recv_ok = {'response': 200}
    test_dict_recv_err = {
        'response': 400,
        'error': 'Bad Request'
    }

    def setUp(self):
        self.connector = Connector()
        self.connector.disconnect()

    def test_send_message(self):
        test_socket = TestSocket(self.test_dict_send)
        self.connector.socket = test_socket
        self.connector.send_message(self.test_dict_send)
        self.assertEqual(self.connector.socket.encoded_message, self.connector.socket.receved_message)
        with self.assertRaises(Exception):
            self.connector.send(test_socket)

    def test_get_message(self):
        test_sock_ok = TestSocket(self.test_dict_recv_ok)
        test_sock_err = TestSocket(self.test_dict_recv_err)
        # тест корректной расшифровки корректного словаря
        self.connector.socket = test_sock_ok
        self.assertEqual(self.connector.get_message(), self.test_dict_recv_ok)
        # тест корректной расшифровки ошибочного словаря
        self.connector.socket = test_sock_err
        self.assertEqual(self.connector.get_message(), self.test_dict_recv_err)


if __name__ == '__main__':
    unittest.main()

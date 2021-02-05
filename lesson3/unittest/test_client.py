import sys
import os
import unittest


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


from common.config import ACTIONS_FLAGS
from client import Client
from socket_simulation import TestSocket

class Tests(unittest.TestCase):
    message = 'test'
    user_to = 'user_to'
    user_from = 'user_from'
    encoding = 'utf-8'
    time = 111111.111111
    room = 'test_room'
    account_name = 'test'

    def setUp(self):
        self.client = Client()
        self.client.disconnect()

    def tearDown(self):
        self.assertEqual(self.client.socket.encoded_message, self.client.socket.receved_message)

    def test_send_message(self):
        self.test_message = {
            "action": ACTIONS_FLAGS['message'],
            "time": self.time,
            "to": self.user_to,
            "from": self.user_from,
            "encoding": self.encoding,
            "message": self.message
        }

        self.client.socket = TestSocket(self.test_message)
        self.client.send_message_from_user(self.message, self.user_to, self.user_from, self.encoding, self.time)

    def test_request_to_join_to_chat(self):
        self.test_message = {
            "action": ACTIONS_FLAGS['join_to_chat'],
            "time": self.time,
            "room": self.room
        }

        self.client.socket = TestSocket(self.test_message)
        self.client.request_to_join_to_chat(self.room, self.time)

    def test_request_to_leave_chat(self):
        self.test_message = {
            "action": ACTIONS_FLAGS['leave_chat'],
            "time": self.time,
            "room": self.room
        }

        self.client.socket = TestSocket(self.test_message)
        self.client.request_to_leave_chat(self.room, self.time)

    def test_send_presense_message(self):
        self.test_message = {
            "action": ACTIONS_FLAGS['presence'],
            "time": self.time,
            'user': {
                'account': self.account_name
            }
        }

        self.client.socket = TestSocket(self.test_message)
        self.client.send_presence_message(self.account_name, self.time)


if __name__ == '__main__':
    unittest.main()

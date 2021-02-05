import sys
import os
import unittest
import json


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


from common.config import ACTIONS_FLAGS, SERVER_MESSAGES, ENCODING
from server import Server
from socket_simulation import TestSocket


class Tests(unittest.TestCase):
    time = 111111.111111
    room = 'test_room'
    account_name = 'test'
    error_code = 400
    alert_code = 200

    presence_message = {
        "action": ACTIONS_FLAGS['presence'],
        "time": time,
        'user': {
            'account': account_name
        }
    }

    join_message = {
        "action": ACTIONS_FLAGS['join_to_chat'],
        "time": time,
        "room": room
    }

    error_message = {
        "time": time,
        "room": room
    }

    error_response = {
                        "response": error_code,
                        "time": time,
                        "error": SERVER_MESSAGES[error_code]
    }

    alert_response = {
                        "response": alert_code,
                        "time": time,
                        "alert": SERVER_MESSAGES[alert_code]
    }

    def setUp(self):
        self.server = Server()
        self.server.disconnect()

    def test_get_response_code(self):
        self.assertEqual(self.server._get_response_code(self.presence_message), 200)
        self.assertEqual(self.server._get_response_code(self.join_message), 400)

    def test_get_response_message(self):
        self.assertEqual(self.server._get_response_message(self.error_code, self.time), self.error_response)
        self.assertEqual(self.server._get_response_message(self.alert_code, self.time), self.alert_response)

    def test_response_to_client(self):
        self.server.socket = TestSocket(self.presence_message)
        self.server.response_to_client(self.time)
        json_alert_response = json.dumps(self.alert_response)
        json_alert_response = json_alert_response.encode(ENCODING)
        self.assertEqual(json_alert_response, self.server.socket.receved_message)

        self.server.socket = TestSocket(self.join_message)
        self.server.response_to_client(self.time)
        json_error_response = json.dumps(self.error_response)
        json_error_response = json_error_response.encode(ENCODING)
        self.assertEqual(json_error_response, self.server.socket.receved_message)


if __name__ == '__main__':
    unittest.main()

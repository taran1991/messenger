import socket
import time
import json
import threading

from common.config import ENCODING, DEFAULT_PORT, DEFAULT_HOST, MAX_PACKAGE_LENGTH
from descripts import Port, Host

# class Connector(threading.Thread):
class Connector(object):
    port = Port()
    host = Host()

    def __init__(self, port=DEFAULT_PORT, host=DEFAULT_HOST, database=None, encoding=ENCODING):
        self.port = port
        self.host = host
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.encoding = encoding
        self.database = database
        super().__init__()

    def disconnect(self):
        self.socket.close()

    def get_str_time(self, default_time=None):
        return_time = default_time if default_time else time.ctime(time.time())
        return return_time

    def get_message(self, client=None):
        if client == None:
            bytes_response = self.socket.recv(MAX_PACKAGE_LENGTH)
        else:
            bytes_response = client.recv(MAX_PACKAGE_LENGTH)
        if isinstance(bytes_response, bytes):
            json_response = bytes_response.decode(self.encoding)
            response = json.loads(json_response)
            if isinstance(response, dict):
                return response
            raise ValueError
        raise ValueError

    def send_message(self, message, sock=None):
        js_message = json.dumps(message)
        encoded_message = js_message.encode(self.encoding)
        if sock == None:
            self.socket.send(encoded_message)
        else:
            sock.send(encoded_message)

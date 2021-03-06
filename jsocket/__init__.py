# This code is modified from https://github.com/mdebbar/jsonsocket

import json
import socket


class Server(object):
    """
    A JSON socket server used to communicate with a JSON socket client. All the
    data is serialized in JSON. How to use it:

    server = Server(host, port)
    while True:
      server.accept()
      data = server.recv()
      # shortcut: data = server.accept().recv()
      server.send({'status': 'ok'})
    """

    backlog = 1000

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(self.backlog)

    def __del__(self):
        self.close()

    def accept(self):
        # if a client is already connected, disconnect it
        client, client_addr = self.socket.accept()
        return client, client_addr

    # def send(self, client, data):
    #     if not client:
    #         raise Exception('Cannot send data, no client is connected')
    #     _send(client.socket, data)
    #     return self

    # def send_and_close(self, client, data):
    #     if not client:
    #         raise Exception('Cannot send data, no client is connected')
    #     _send(client.socket, data)
    #     client.close()
    #     return self

    def recv(self, client):
        if not client:
            raise Exception('Cannot receive data, no client is connected')
        return _recv(client)
    
    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None


class Client(object):
    """
    A JSON socket client used to communicate with a JSON socket server. All the
    data is serialized in JSON. How to use it:

    data = {
      'name': 'Patrick Jane',
      'age': 45,
      'children': ['Susie', 'Mike', 'Philip']
    }
    client = Client()
    client.connect(host, port)
    client.send(data)
    response = client.recv()
    # or in one line:
    response = Client().connect(host, port).send(data).recv()
    """

    socket = None

    def __del__(self):
        self.close()

    def connect(self, host_port):
        host = host_port.split(':')[0]
        port = int(host_port.split(':')[1])
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return self

    def send(self, data):
        if not self.socket:
            raise Exception('You have to connect first before sending data')
        _send(self.socket, data)
        return self

    def recv(self):
        if not self.socket:
            raise Exception('You have to connect first before receiving data')
        return _recv(self.socket)
    
    def recv_socket(self, size):
        if not self.socket:
            raise Exception('No socket')
        return self.socket.recv(size)
 
    def recv_and_close(self):
        data = self.recv()
        self.close()
        return data

    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None


## helper functions ##

def _send(socket, data):
    try:
        serialized = json.dumps(data)
    except (TypeError, ValueError), e:
        raise Exception('You can only send JSON-serializable data')
    # send the length of the serialized data first
    socket.send('%d\n' % len(serialized))
    # send the serialized data
    socket.sendall(serialized)


def _recv(socket):
    # read the length of the data, letter by letter until we reach EOL
    length_str = ''
    char = socket.recv(1)
    if char == '':
        return ''
    while char != '\n':
        length_str += char
        char = socket.recv(1)
    total = int(length_str)
    # use a memoryview to receive the data chunk by chunk efficiently
    view = memoryview(bytearray(total))
    next_offset = 0
    while total - next_offset > 0:
        recv_size = socket.recv_into(view[next_offset:], total - next_offset)
        next_offset += recv_size
    try:
        deserialized = json.loads(view.tobytes())
    except (TypeError, ValueError), e:
        raise Exception('Data received was not in JSON format')
    return deserialized

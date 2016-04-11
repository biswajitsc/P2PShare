import socket
import jsocket
import constants
import time


class Server:
    conn = None
    active_peers = set()

    def __init__(self):
        print 'Server running'
        self.conn = jsocket.Server('localhost', constants.FILES_LISTEN_PORT)

    def run(self):
        while True:
            self.conn.accept()
            data = self.conn.recv()
            if data['type'] == 'I_AM_ONLINE':
                self.conn.send(self.get_peers())

    def get_peers(self):
        peer_list = {}
        cnt = 0
        for p in self.active_peers:
            peer_list['peer'+cnt] = p
        return peer_list

    def file_list_manager(self, data):
        for f in data.keylist():
            if f.startswith('file'):
                f = data[f]
                self.file_list.insert(f)
                self.file_time = time.time()

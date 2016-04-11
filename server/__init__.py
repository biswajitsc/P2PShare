import socket
import jsocket
import constants
import time
import threading
import thread


class Server:
    conn = None
    active_peers = set()

    def __init__(self):
        print 'Server running'
        self.conn = jsocket.Server('localhost', constants.LOGIN_PORT)

    def run(self):
        while True:
            self.conn.accept()
            data = self.conn.recv()
            if data['type'] == 'GET_PEERS':
                thread.start_new_thread(self.conn.send, (self.get_peers(),))
            if data['type'] == 'PEER_OFFLINE':
                thread.start_new_thread(self.peer_offline, (data['peer'],))

    def get_peers(self):
        peer_list = {}
        cnt = 0
        for p in self.active_peers:
            peer_list['peer' + cnt] = p
        return peer_list

    def file_list_manager(self, data):
        for f in data.keylist():
            if f.startswith('file'):
                f = data[f]
                self.file_list.insert(f)
                self.file_time = time.time()

    def peer_offline():
        pass

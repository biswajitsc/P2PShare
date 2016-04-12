import socket
import jsocket
import constants
import time
import threading
import thread


class Server:
    conn = None

    active_peers = set()
    active_peers_lock = threading.Lock()

    def __init__(self):
        print 'Server running'
        self.sock = jsocket.Server('localhost', constants.LOGIN_PORT)

    def run(self):
        while True:
            conn = self.sock.accept()
            data = self.conn.recv(conn)
            if data['type'] == 'GET_PEERS':
                thread.start_new_thread(
                    self.sock.send_and_close, (self.client, self.get_peers(),))
            if data['type'] == 'PEER_OFFLINE':
                thread.start_new_thread(self.peer_offline, (data['peer'],))

    def get_peers(self):
        peer_list = {}
        cnt = 0
        for p in self.active_peers:
            peer_list['peer' + cnt] = p
        return peer_list

    def peer_offline(self, peer_id):
        self.active_peers_lock.acquire()
        self.active_peers.discard(peer_id)
        self.active_peers_lock.release()

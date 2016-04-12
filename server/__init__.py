import socket
import jsocket
import constants
import time
import threading
import thread
import sleep

class Server:
    active_peers = set()
    active_peers_lock = threading.Lock()

    def __init__(self):
        print 'Server running'
        self.sock = jsocket.Server('localhost', constants.LOGIN_PORT)

    def run(self):
        thread.start_new_thread(self.heartbeat, ())
        while True:
            conn = self.sock.accept()
            data = self.conn.recv(conn)
            node_id = data['node_id']
            if data['type'] == 'I_AM_ONLINE':
                if self.peer_eligible(node_id):
                    thread.start_new_thread(
                        self.sock.send_and_close,
                        (conn, {'type': 'YOU_ARE_PEER'})
                    )
                else:
                    conn.close()
            if data['type'] == 'GET_PEERS':
                thread.start_new_thread(
                    self.sock.send_and_close, (conn, self.get_peers(),))
            if data['type'] == 'PEER_OFFLINE':
                thread.start_new_thread(self.peer_offline, (data['peer_id'],))
            if data['type'] == 'I_AM_PEER':
                thread.start_new_thread(self.add_peer, (node_id, ))
            else:
                conn.close()

    def get_peers(self):
        peer_list = {}
        cnt = 0
        for p in self.active_peers:
            peer_list['peer' + cnt] = p
        return peer_list

    def add_peers(self, node_id):
        self.active_peers_lock.acquire()
        self.active_peers.add(node_id)
        self.active_peers_lock.release()

    def peer_offline(self, peer_id):
        self.active_peers_lock.acquire()
        self.active_peers.discard(peer_id)
        self.active_peers_lock.release()

    def peer_eligible(self, node_id):
        self.active_peers_lock.acquire()
        if len(self.active_peers) < constants.MAX_PEERS:
            return True

    def heartbeat(self):
        while True:
            sec_start = time.time()
            for peer in self.active_peers:
                sock = jsocket.Client()
                try:
                    sock.connect('localhost', peer)
                    sock.send({'type': 'ARE_YOU_ALIVE'})
                    sock.recv_and_close()
                except Exception as e:
                    print e
                    self.active_peers_lock.acquire()
                    self.active_peers.discard(peer)
                    self.active_peers_lock.release()
            time.sleep(max(0, 60 - (time.time() - sec_start)))

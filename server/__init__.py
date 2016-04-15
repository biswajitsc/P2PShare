import socket
import jsocket
import constants
import time
import threading
import thread
import random
import math


class Server:

    def __init__(self):
        self.active_peers = set()
        self.active_peers_timestamps = {}
        self.active_peers_lock = threading.Lock()

        self.normal_nodes = set()
        self.normal_nodes_timestamps = {}
        self.normal_node_lock = threading.Lock()

        self.sock = jsocket.Server('localhost', constants.LOGIN_PORT)
        self.node_id = constants.LOGIN_PORT

    def run(self):
        print 'Server running'

        thread_obj = threading.Thread(target=self.peer_heartbeat)
        thread_obj.setDaemon(True)
        thread_obj.start()

        thread_obj = threading.Thread(target=self.normal_heartbeat)
        thread_obj.setDaemon(True)
        thread_obj.start()

        while True:
            conn, dummy = self.sock.accept()
            # print conn
            data = self.sock.recv(conn)
            print_msg_info(data)
            conn.close()

            inc_id = int(data['node_id'])
            msg_type = data['type'].strip()

            if msg_type == 'I_AM_ONLINE':
                if self.peer_eligible(inc_id):
                    thread.start_new_thread(self.add_normal_node, (inc_id,))

            elif msg_type == 'GET_PEERS_WRITE':
                thread.start_new_thread(self.get_peers_write, (inc_id,))

            elif msg_type == 'GET_PEERS_READ':
                thread.start_new_thread(self.get_peers_read, (inc_id,))

            elif msg_type == 'I_AM_PEER':
                thread.start_new_thread(self.add_peer, (inc_id,))

            elif msg_type == 'I_AM_ALIVE':
                thread.start_new_thread(self.update_peer, (inc_id,))

            else:
                print 'Unidentified message type {}'.format(msg_type)
                # conn.close()

    def get_peers_read(self):
        conn = jsocket.Client()
        conn.connect('localhost', inc_id)
        print constants.SUPER_PEER_TAG, 'entered GET_PEERS_READ'
        self.normal_node_lock.acquire()
        self.normal_nodes_timestamps[inc_id] = time.time()
        self.normal_node_lock.release()

        self.active_peers_lock.acquire()
        peer_list = []
        if len(self.active_peers) > 0:
            sample_peers = random.sample(
                self.active_peers, int(math.floor(len(self.active_peers) / 2)) + 1)
            for p in sample_peers:
                peer_list.append(p)
        else:
            print '0 sample peers'
        self.active_peers_lock.release()
        conn.send(
            {'type': 'YOUR_READ_PEERS', 'node_id': self.node_id, 'peers': peer_list})
        conn.close()
        print constants.SUPER_PEER_TAG, 'exiting get_peers_read function'

    def get_peers_write(self, inc_id):
        conn = jsocket.Client()
        conn.connect('localhost', inc_id)
        print constants.SUPER_PEER_TAG, 'entered GET_PEERS_WRITE'
        self.normal_node_lock.acquire()
        self.normal_nodes_timestamps[inc_id] = time.time()
        self.normal_node_lock.release()

        self.active_peers_lock.acquire()
        peer_list = []
        if len(self.active_peers) > 0:
            sample_peers = random.sample(
                self.active_peers, int(math.floor(len(self.active_peers) / 2)) + 1)
            for p in sample_peers:
                peer_list.append(p)
        else:
            print '0 sample peers'
        self.active_peers_lock.release()
        conn.send(
            {'type': 'YOUR_WRITE_PEERS', 'node_id': self.node_id, 'peers': peer_list})
        conn.close()
        print constants.SUPER_PEER_TAG, 'exiting get_peers_write function'

    def add_peer(self, inc_id):
        conn = jsocket.Client()
        conn.connect('localhost', inc_id)

        if node_id in self.active_peers:
            conn.send({'type': 'ALREADY_PEER', 'node_id': self.node_id})
            conn.close()
        else:
            conn.send({'type': 'ACK', 'node_id': self.node_id})
            conn.close()
            self.active_peers_lock.acquire()
            self.active_peers.add(node_id)
            self.active_peers_timestamps[node_id] = time.time()
            self.active_peers_lock.release()

    def add_normal_node(self, node_id):
        self.normal_node_lock.acquire()
        self.normal_nodes.add(node_id)
        self.normal_nodes_timestamps[node_id] = time.time()
        self.normal_node_lock.release()

    def peer_eligible(self, node_id):
        if node_id > 8000 and node_id < 8050:

            return True

    def update_peer(self, node_id):
        self.active_peers_lock.acquire()
        self.active_peers.add(node_id)
        self.active_peers_timestamps[node_id] = time.time()
        self.active_peers_lock.release()

    def peer_heartbeat(self):
        while True:
            print constants.SUPER_PEER_TAG, 'Cleaning peer nodes'
            self.active_peers_lock.acquire()
            new_peer = {}

            for peer_i, last_access in self.active_peers_timestamps.items():
                if time.time() - last_access > constants.MAX_OFFLINE_TIME:
                    try:
                        self.active_peers.discard(peer_i)
                    except Exception:
                        continue
                else:
                    new_peer[peer_i] = last_access

            self.active_peers_timestamps = new_peer
            self.active_peers_lock.release()
            time.sleep(constants.MAX_OFFLINE_TIME)

    def normal_heartbeat(self):
        while True:
            print constants.SUPER_PEER_TAG, 'Cleaning normal nodes'
            self.normal_node_lock.acquire()
            new_normal = {}
            for normal, last_access in self.normal_nodes_timestamps.items():
                if time.time() - last_access > constants.MAX_OFFLINE_TIME:
                    try:
                        self.normal_nodes.discard(normal)
                    except Exception:
                        continue
                else:
                    new_normal[normal] = last_access

            self.normal_nodes_timestamps = new_normal
            self.normal_node_lock.release()
            time.sleep(constants.MAX_OFFLINE_TIME)


def print_msg_info(data):
    print constants.SUPER_PEER_TAG,
    print 'Received {} from {}.'.format(data['type'], data['node_id'])

import socket
import jsocket
import constants
import time
import threading
import thread
import random
import math


class Server:

    def __init__(self, node_id, other_id):

        self.active_peers = set()
        self.active_peers_timestamps = {}
        self.active_peers_lock = threading.Lock()

        self.normal_nodes = set()
        self.normal_nodes_timestamps = {}
        self.normal_nodes_lock = threading.Lock()

        self.node_id = node_id
        self._node_port = int(node_id.split(':')[1])
        self._node_ip = node_id.split(':')[0]
        self.other_id = other_id

        self.sock = jsocket.Server(self._node_ip, self._node_port)

    def run(self):
        print constants.SUPER_PEER_TAG(self.node_id), 'Server running'

        thread_obj = threading.Thread(target=self.peer_heartbeat)
        thread_obj.setDaemon(True)
        thread_obj.start()

        thread_obj = threading.Thread(target=self.normal_heartbeat)
        thread_obj.setDaemon(True)
        thread_obj.start()

        thread_obj = threading.Thread(target=self.select_peers)
        thread_obj.setDaemon(True)
        thread_obj.start()

        while True:
            conn, dummy = self.sock.accept()
            # print conn
            data = self.sock.recv(conn)
            self.print_msg_info(data)
            conn.close()

            inc_id = data['node_id']
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

            elif msg_type == 'APT':
                thread.start_new_thread(
                    self.sync_listener_thread, (data['data'], 'APT'))

            elif msg_type == 'NNT':
                thread.start_new_thread(
                    self.sync_listener_thread, (data['data'], 'NNT'))

            else:
                print 'Unidentified message type {}'.format(msg_type)
                # conn.close()

    def sync_listener_thread(self, data, mode):
        print constants.SUPER_PEER_TAG(self.node_id), 'Syncing state'
        if mode == 'APT':
            self.active_peers_lock.acquire()
            for peer, timestamp in data.items():
                if peer not in self.active_peers_timestamps.keys():
                    self.active_peers_timestamps[peer] = timestamp
                else:
                    self.active_peers_timestamps[peer] = max(
                        self.active_peers_timestamps[peer], timestamp)
            self.active_peers_lock.release()
        if mode == 'NNT':
            self.normal_nodes_lock.acquire()
            for normal, timestamp in data.items():
                if normal not in self.normal_nodes_timestamps.keys():
                    self.normal_nodes_timestamps[normal] = timestamp
                else:
                    self.normal_nodes_timestamps[normal] = max(
                        self.normal_nodes_timestamps[normal], timestamp)
            self.normal_nodes_lock.release()

    def get_peers_read(self, inc_id):
        conn = jsocket.Client()
        conn.connect(inc_id)
        print constants.SUPER_PEER_TAG(self.node_id), 'Read Peers asked by', inc_id
        # print constants.SUPER_PEER_TAG(self.node_id), 'entered GET_PEERS_READ'
        self.normal_nodes_lock.acquire()
        self.normal_nodes_timestamps[inc_id] = time.time()
        self.normal_nodes_lock.release()

        self.active_peers_lock.acquire()
        peer_list = []
        if len(self.active_peers) > 0:
            # sample_peers = random.sample(
            # self.active_peers, int(math.floor(len(self.active_peers) / 2)) +
            # 1)
            sample_peers = random.sample(
                self.active_peers, constants.GET_PEER_READ_SIZE(len(self.active_peers)))
            for p in sample_peers:
                peer_list.append(p)
        else:
            print constants.SUPER_PEER_TAG(self.node_id), 'No eligible read peers found'
            # print '0 sample peers'
        self.active_peers_lock.release()
        conn.send(
            {'type': 'YOUR_READ_PEERS', 'node_id': self.node_id, 'peers': peer_list})
        conn.close()
        print constants.SUPER_PEER_TAG(self.node_id), 'exiting get_peers_read function'

    def get_peers_write(self, inc_id):
        print constants.SUPER_PEER_TAG(self.node_id), 'Write Peers asked by', inc_id
        # print constants.SUPER_PEER_TAG(self.node_id), 'entered GET_PEERS_WRITE'
        self.normal_nodes_lock.acquire()
        self.normal_nodes_timestamps[inc_id] = time.time()
        self.normal_nodes_lock.release()

        self.active_peers_lock.acquire()
        peer_list = []
        if len(self.active_peers) > 0:
            # sample_peers = random.sample(
            # self.active_peers, int(math.floor(len(self.active_peers) / 2)) +
            # 1)
            sample_peers = random.sample(
                self.active_peers, constants.GET_PEER_WRITE_SIZE(len(self.active_peers)))
            for p in sample_peers:
                peer_list.append(p)
        else:
            print constants.SUPER_PEER_TAG(self.node_id), 'No eligible write peers found'
        self.active_peers_lock.release()

        conn = jsocket.Client()
        # print inc_id
        conn.connect(inc_id)
        conn.send({
            'type': 'YOUR_WRITE_PEERS',
            'node_id': self.node_id,
            'peers': peer_list
        })
        conn.close()
        # print constants.SUPER_PEER_TAG(self.node_id), 'exiting get_peers_write function'

    def add_peer(self, inc_id):
        if inc_id not in self.active_peers:
            self.active_peers_lock.acquire()
            self.active_peers.add(inc_id)
            self.active_peers_timestamps[inc_id] = time.time()
            self.active_peers_lock.release()

    def add_normal_node(self, node_id):
        self.normal_nodes_lock.acquire()
        self.normal_nodes.add(node_id)
        self.normal_nodes_timestamps[node_id] = time.time()
        self.normal_nodes_lock.release()

    def peer_eligible(self, node_id):
        port = int(node_id.split(':')[1])
        print constants.SUPER_PEER_TAG(self.node_id), port
        if port > 8000 and port < 8050:
            return True

    def update_peer(self, node_id):
        self.active_peers_lock.acquire()
        self.active_peers.add(node_id)
        self.active_peers_timestamps[node_id] = time.time()
        self.active_peers_lock.release()

    def peer_heartbeat(self):
        while True:
            print constants.SUPER_PEER_TAG(self.node_id), 'Cleaning peer nodes'
            print constants.SUPER_PEER_TAG(self.node_id), 'Current peer list : ', self.active_peers
            self.active_peers_lock.acquire()
            new_peer = {}

            for peer_i, last_access in self.active_peers_timestamps.items():
                print constants.SUPER_PEER_TAG(self.node_id), "Peer ", peer_i, " is unreachable for ", time.time() - last_access
                if time.time() - last_access > constants.MAX_OFFLINE_TIME():
                    try:
                        self.active_peers.discard(peer_i)
                        print constants.SUPER_PEER_TAG(self.node_id), peer_i, "discarded"
                    except Exception:
                        continue
                else:
                    new_peer[peer_i] = last_access
                    self.active_peers.add(peer_i)

            self.active_peers_timestamps = new_peer
            print constants.SUPER_PEER_TAG(self.node_id), 'Cleaning peer nodes done'
            print constants.SUPER_PEER_TAG(self.node_id), 'Cleaned peer list : ', self.active_peers

            try:
                conn = jsocket.Client()
                conn.connect(self.other_id)
                conn.send({
                    'type': 'APT',
                    'node_id': self.node_id,
                    'data': new_peer
                })
                conn.close()
            except:
                print constants.SUPER_PEER_TAG(self.node_id), 'Other server seems down'

            self.active_peers_lock.release()
            time.sleep(constants.HEARTBEAT_TIMEOUT())

    def normal_heartbeat(self):
        while True:
            print constants.SUPER_PEER_TAG(self.node_id), 'Cleaning normal nodes'
            print constants.SUPER_PEER_TAG(self.node_id), 'Current normal node list : ', self.normal_nodes
            self.normal_nodes_lock.acquire()
            new_normal = {}
            for normal, last_access in self.normal_nodes_timestamps.items():
                print constants.SUPER_PEER_TAG(self.node_id), "Normal node ", normal, "is unreachable for ", time.time() - last_access
                if time.time() - last_access > constants.MAX_OFFLINE_TIME():
                    try:
                        print constants.SUPER_PEER_TAG(self.node_id), normal
                        self.normal_nodes.discard(normal)
                    except Exception:
                        continue
                else:
                    new_normal[normal] = last_access
                    if self.peer_eligible(normal):
                        self.normal_nodes.add(normal)

            self.normal_nodes_timestamps = new_normal
            print constants.SUPER_PEER_TAG(self.node_id), 'Cleaning normal nodes done'
            print constants.SUPER_PEER_TAG(self.node_id), 'Cleaned normal node list : ', self.normal_nodes

            try:
                conn = jsocket.Client()
                conn.connect(self.other_id)
                conn.send({
                    'type': 'NNT',
                    'node_id': self.node_id,
                    'data': new_normal
                })
                conn.close()
            except:
                print constants.SUPER_PEER_TAG(self.node_id), 'Other server seems down'

            self.normal_nodes_lock.release()
            time.sleep(constants.HEARTBEAT_TIMEOUT())

    def select_peers(self):
        while True:
            print constants.SUPER_PEER_TAG(self.node_id), 'Selecting Peers'
            self.active_peers_lock.acquire()
            self.normal_nodes_lock.acquire()

            print constants.SUPER_PEER_TAG(self.node_id), 'Current peer list : ', self.active_peers
            print constants.SUPER_PEER_TAG(self.node_id), 'Current normal node list : ', self.normal_nodes

            if len(self.active_peers) < constants.MAX_PEERS(len(self.normal_nodes)):
                new_peer_length = max(
                    0, constants.MAX_PEERS(len(self.normal_nodes)) - len(self.active_peers))
                print constants.SUPER_PEER_TAG(self.node_id), new_peer_length
                print constants.SUPER_PEER_TAG(self.node_id), self.normal_nodes
                print constants.SUPER_PEER_TAG(self.node_id), self.active_peers
                new_peer_length = min(
                    new_peer_length, len(self.normal_nodes - self.active_peers))
                new_peers = random.sample(
                    self.normal_nodes - self.active_peers, new_peer_length)
                print constants.SUPER_PEER_TAG(self.node_id), new_peer_length
                for p in new_peers:
                    try:
                        print constants.SUPER_PEER_TAG(self.node_id), 'selecting peer : ', p
                        conn = jsocket.Client()
                        conn.connect(p)
                        conn.send(
                            {'type': 'YOU_ARE_PEER', 'node_id': self.node_id})
                        conn.close()
                        # self.active_peers.add(int(p) + 1)
                    except Exception:
                        print constants.SUPER_PEER_TAG(self.node_id), 'peer ', p, 'is down'
                        conn.close()

            print constants.SUPER_PEER_TAG(self.node_id), 'Selecting Peers Done'
            print constants.SUPER_PEER_TAG(self.node_id), 'New peer list : ', self.active_peers
            self.normal_nodes_lock.release()
            self.active_peers_lock.release()

            time.sleep(constants.SELECT_PEER_TIMEOUT())

    def print_msg_info(self, data):
        print constants.SUPER_PEER_TAG(self.node_id),
        print 'Received {} from {}.'.format(data['type'], data['node_id'])

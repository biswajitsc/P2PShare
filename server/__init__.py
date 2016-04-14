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
        print 'Server running'
        self.active_peers = set()
        self.normal_nodes = set()
        self.normal_nodes_timestamps = {}
        self.active_peers_lock = threading.Lock()
        self.sock = jsocket.Server('localhost', constants.LOGIN_PORT)
        self.node_id = constants.LOGIN_PORT
        # print self.sock

    def run(self):
        thread.start_new_thread(self.heartbeat, ())
        thread.start_new_thread(self.clean_normal_nodes, ())
        while True:
            conn,dummy = self.sock.accept()
            # print conn
            data = self.sock.recv(conn)
            print_msg_info(data)
            conn.close()

            inc_id = int(data['node_id'])
            msg_type = data['type'].strip()
            
            conn = jsocket.Client()
            conn.connect('localhost', inc_id)
            
            if msg_type == 'I_AM_ONLINE':
                if self.peer_eligible(inc_id):
                    thread.start_new_thread(
                        self.sock.send_and_close,
                        (conn, {
                            'type': 'YOU_ARE_PEER',
                            'node_id': self.node_id
                        })
                    )
                else:
                    conn.close()
            elif msg_type == 'GET_PEERS_WRITE':
                print constants.SUPER_PEER_TAG, 'entered GET_PEERS_WRITE'
                self.active_peers_lock.acquire()
                self.normal_nodes_timestamps[inc_id] = time.time()
                self.active_peers_lock.release()
                print constants.SUPER_PEER_TAG, 'calling GET_PEERS_WRITE thread'
                
                thread.start_new_thread(
                    self.sock.send_and_close, 
                    (conn, {
                        'type': 'YOUR_PEERS_WRITE',
                        'node_id': self.node_id,
                        'data': self.get_peers_write()
                        })
                    )

            elif msg_type == 'GET_PEERS_READ':
                thread.start_new_thread(
                    self.sock.send_and_close, 
                    (conn, {
                        'type': 'YOUR_PEERS_READ',
                        'node_id': self.node_id,
                        'data': self.get_peers_read()
                        })
                    )
            elif msg_type == 'PEER_OFFLINE':
                thread.start_new_thread(self.peer_offline, (data['peer_id'],))
                conn.close()
            elif msg_type == 'I_AM_PEER':
                thread.start_new_thread(self.add_peer, (inc_id, conn))
            else:
                print 'Unidentified message type {}'.format(msg_type)
                conn.close()

    def get_peers_read(self):
        self.active_peers_lock.acquire()
        peer_list = {}
        peer_list['peers'] = []
        if len(self.active_peers) > 0:
            sample_peers = random.sample(self.active_peers, int(math.floor(len(self.active_peers)/2))+1)
            for p in sample_peers:
                peer_list['peers'].append(p)
        else:
            print '0 sample peers'
        self.active_peers_lock.release()
        return peer_list
    
    def get_peers_write(self):
        print constants.SUPER_PEER_TAG, 'inside get_peers_write function'
        print constants.SUPER_PEER_TAG, self.active_peers
        self.active_peers_lock.acquire()
        peer_list = {}
        peer_list['peers'] = []
        if len(self.active_peers) > 0:
            sample_peers = random.sample(self.active_peers, int(math.floor(len(self.active_peers)/2))+1)
            for p in sample_peers:
                peer_list['peers'].append(p)
        else:
            print '0 sample peers'
        self.active_peers_lock.release()
        print constants.SUPER_PEER_TAG, 'peer_list', peer_list
        return peer_list

    def add_peer(self, node_id, conn):
        if node_id in self.active_peers:
            self.sock.send_and_close(conn, {'type': 'ALREADY_PEER', 'node_id': self.node_id})
        else:
            self.sock.send_and_close(conn, {'type': 'ACK', 'node_id': self.node_id})
            self.active_peers_lock.acquire()
            self.active_peers.add(node_id)
            self.active_peers_lock.release()

    def peer_offline(self, peer_id):
        self.active_peers_lock.acquire()
        self.active_peers.discard(peer_id)
        self.active_peers_lock.release()

    def peer_eligible(self, node_id):
        self.active_peers_lock.acquire()
        self.normal_nodes.add(node_id)
        flag = False
        if len(self.active_peers) < constants.MAX_PEERS:
            self.active_peers.add(node_id+1)
            print constants.SUPER_PEER_TAG,'Added node_id',node_id+1
            flag = True
        self.active_peers_lock.release()
        return flag

    def heartbeat(self):
        while True:
            sec_start = time.time()
            self.active_peers_lock.acquire()
            dummy_peers = self.active_peers
            for peer in dummy_peers:
                sock = jsocket.Client()
                try:
                    sock.connect('localhost', peer)
                    sock.send({'type': 'ARE_YOU_ALIVE', 'node_id': self.node_id})
                    sock.recv_and_close()
                    print constants.SUPER_PEER_TAG, 
                    print 'Peer Node {} is ONLINE.'.format(peer)
                except Exception:
                    print 'Peer Node {} is OFFLINE.'.format(peer)
                    self.active_peers.discard(peer)
            self.active_peers_lock.release()
            
            if len(self.active_peers) < constants.MAX_PEERS:
                self.active_peers_lock.acquire()
                new_peer_length = max(0,constants.MAX_PEERS - len(self.active_peers))
                new_peer_length = min(new_peer_length, len(self.normal_nodes - self.active_peers))
                new_peers = random.sample(self.normal_nodes - self.active_peers, new_peer_length)
                
                for p in new_peers:
                    sock = jsocket.Client()
                    sock.connect('localhost', int(p))
                    sock.send({ 'type': 'YOU_ARE_PEER', 'node_id': self.node_id })
                    sock.close()
                    self.active_peers.add(int(p)+1)

                self.active_peers_lock.release()
            
            time.sleep(max(0,constants.INVALIDATE_TIMEOUT - (time.time() - sec_start)))

    def clean_normal_nodes(self):
        while True:
            self.active_peers_lock.acquire()
            new_normal = {}
            for normal,last_access in self.normal_nodes_timestamps.items():
                if time.time() - last_access > constants.MAX_OFFLINE_TIME:
                    new_normal[normal] = last_access
                    self.normal_nodes.discard(normal)
            self.normal_nodes_timestamps = new_normal
            self.active_peers_lock.release()
            time.sleep(60)

def print_msg_info(data):
    print constants.SUPER_PEER_TAG,
    print 'Received {} from {}.'.format(data['type'], data['node_id'])

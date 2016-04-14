import os
import peer
import threading
import jsocket
import thread
import time
import constants

# Threads of Normal Node
# -> Input (Commands like Search and Download)
# -> Listen at port (e.g. YOU_ARE_PEER, Download its file)
#   -> If peer, start a new thread for Peer
# -> Periodically refresh file list, get peer and share

class NormalNode(threading.Thread):
    def __init__(self, id):
        self._node_id = id
        self._is_peer = False
        self._search_string = None
        self._search_results = []
        threading.Thread.__init__(self)
        print 'Creating normal node'
        self._conn = jsocket.Client()
        self._shared_folder = 'Share/' + str(self._node_id)
        print 'Shared folder', self._shared_folder
        self._conn.connect('localhost', constants.LOGIN_PORT)
        self._conn.send({
                'type': 'I_AM_ONLINE',
                'node_id': self._node_id
            })
        self._conn.close()
        self._sock = jsocket.Server('localhost', self._node_id)

    def run(self):
        thread.start_new_thread(self._listen, ())
        thread.start_new_thread(self._auto_get_write_peers, ())
        while True:
            print '$',
            command = raw_input().strip().split()
            if command[0] == 'search':
                # Send file to peers, wait for response
                if len(command) < 2:
                    raise ValueError('Search string not provided')
                self._search_string = command[1]
            elif command[0] == 'download':
                # Download the given file
                if len(command) < 2:
                    raise ValueError('Search string not provided')
                try:
                    id = int(command[1])
                    self._download_path = self._search_results[id]
                except Exception as e:
                    print 'Invalid id'
            elif command[0] == 'help':
                print 'search   [filename] : Search for a file'
                print 'download [id]       : Download a file from the search results'
            else:
                print 'Invalid command. Type help for the list of commands'
    
    def _listen(self):
        while True:
            conn, dummy = self._sock.accept()
            data = self._sock.recv(conn)
            print "Data is : "
            print data
            incoming_id = int(data['node_id'])
            msg_type = data['type']

            if msg_type == 'YOU_ARE_PEER':
                # Its a peer, if already its a peer ignore
                # Otherwise start a new thread for peer
                if not self._is_peer:
                    self._is_peer = True
                    self_peer = peer.Peer(self._node_id + 1)
                    self_peer.daemon = True
                    self_peer.start()
                    self_peer.join()
            elif msg_type == 'DOWNLOAD':
                # Some one wants to download one of its files
                pass
            elif msg_type == 'YOUR_READ_PEERS':
                # Get the peer list and send them its file list
                if self._search_string is not None:
                    peers = data['peers']
                    for p in peers:
                        self._conn.connect('localhost', p)
                        self._conn.send({
                                'type': 'SEARCH',
                                'node_id': self._node_id,
                                'query': self._search_string
                            })
                        self._conn.close()
                    self._search_string = None
            elif msg_type == 'YOUR_WRITE_PEERS':
                # Get the peer list and send them its file list
                peers = data['peers']
                file_list = []
                for (dir_path, dir_names, file_names) in os.walk(self._shared_folder):
                    file_list.extend(file_names)
                for p in peers:
                    self._conn.connect('localhost', p)
                    self._conn.send({
                            'type': 'SHARE_MY_FILES',
                            'node_id': self._node_id,
                            'shared_files': file_list
                        })
                    self._conn.close()
            else:
                print 'Unidentified message type {}'.format(msg_type)

    def _auto_get_write_peers(self):
        time.sleep(1)
        while True:
            self._conn.connect('localhost', constants.LOGIN_PORT)
            self._conn.send({
                    'type': 'GET_PEERS_WRITE',
                    'node_id': self._node_id
                })
            self._conn.close()
            time.sleep(120)

    def _get_read_peers(self):
        self._conn.connect('localhost', constants.LOGIN_PORT)
        self._conn.send({
                'type': 'GET_PEERS_READ',
                'node_id': self._node_id
            })
        self._conn.close()

    def _print_msg_info(data):
        print 'Recieved {} from {}.'.format(data['type'], data['node_id'])

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
        thread.start_new_thread(self._get_read_peers, ())
        while True:
            print '$',
            command = raw_input().strip().split()
            if command[0] == 'search':
                # Send file to peers, wait for response
                pass
            elif command[0] == 'download':
                # Download the given file
                pass
            elif command[0] == 'help':
                print 'search   [filename] : Search for a file'
                print 'download [id]       : Download a file from the search results'
            else:
                print 'Invalid command. Type help for the list of commands'
    
    def _listen(self):
        while True:
            conn,dummy = self._sock.accept()
            data = self._sock.recv(conn)
            print "Data is : "
            print data
            incoming_id = int(data['node_id'])
            msg_type = data['type']

            if msg_type == 'YOU_ARE_PEER':
                # Its a peer, if already its a peer ignore
                # Otherwise start a new thread for peer
                self._is_peer = True
            elif msg_type == 'DOWNLOAD':
                # Some one wants to download one of its files
                pass
            elif msg_type == 'YOUR_PEERS':
                # Get the peer list and send them its file list
                pass
            else:
                print 'Unidentified message type {}'.format(msg_type)

    def _auto_get_write_peers(self):
        time.sleep(1)
        while True:
            file_list = []
            for (dir_path, dir_names, file_names) in os.walk(self._shared_folder):
                file_list.extend(file_names)
            self._conn.connect('localhost', constants.LOGIN_PORT)
            self._conn.send({
                    'type': 'GET_PEERS',
                    'node_id': self._node_id
                })
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

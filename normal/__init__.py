import os
import peer
import threading
import jsocket
import thread
import time
import constants

'''
Threads of Normal Node
-> Input (Commands like Search and Download)
-> Listen at port (e.g. YOU_ARE_PEER, Download its file)
  -> If peer, start a new thread for Peer
-> Periodically refresh file list, get peer and share
'''


class NormalNode(threading.Thread):
    def __init__(self, id):
        self._node_id = id
        self._is_peer = False
        self._search_string = None
        self._search_results = []
        super(NormalNode, self).__init__()
        print constants.NORMAL_TAG, 'Creating normal node'

        self._log_file = open('log.txt', 'a')
        conn = jsocket.Client()

        self._shared_folder = os.path.join('Share', str(self._node_id))
        self._make_sure_exits('Share')
        self._make_sure_exits(self._shared_folder)

        self._download_folder = os.path.join('Download', str(self._node_id))
        self._make_sure_exits('Download')
        self._make_sure_exits(self._download_folder)

        print >> self._log_file, constants.NORMAL_TAG, 'Shared folder', self._shared_folder
        self._sock = jsocket.Server('localhost', self._node_id)

        conn.connect('localhost', constants.LOGIN_PORT)
        conn.send({
            'type': 'I_AM_ONLINE',
            'node_id': self._node_id
        })
        print >> self._log_file, constants.NORMAL_TAG, 'Sent I_AM_ONLINE'
        conn.close()

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
                self._get_read_peers()

            elif command[0] == 'download':
                # Download the given file
                if len(command) < 2:
                    raise ValueError('Download id not provided')
                result = None
                try:
                    result = self._search_results[int(command[1])]
                except Exception:
                    print 'Invalid id'
                conn = jsocket.Client()
                conn.connect('localhost', result[1])
                conn.send({
                    'type': 'DOWNLOAD',
                    'node_id': self._node_id,
                    'file_path': result[0]
                })
                print 'Enter file name'
                file_name = raw_input().strip()
                print constants.NORMAL_TAG, 'Downloading from', result[1], 'to', file_name
                with open(os.path.join(self._shared_folder, file_name), 'wb') as file_to_write:
                    while True:
                        data_read = conn.recv(BUFFER_SIZE)
                        if not data_read:
                            break
                        file_to_write.write(data_read)
                    file_to_write.close()
                conn.close()

            elif command[0] == 'help':
                print 'search   [filename] : Search for a file'
                print 'download [id]       : Download a file from the search results'

            else:
                print 'Invalid command. Type \'help\' for the list of commands'

    def _listen(self):
        while True:
            print >> self._log_file, constants.NORMAL_TAG, 'Waiting for connection'
            data = ''
            conn, dummy = self._sock.accept()
            data = self._sock.recv(conn)
            conn.close()
            if data == '':
                continue

            print >> self._log_file, constants.NORMAL_TAG, "Data is : ",
            print >> self._log_file, data
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

            elif msg_type == 'SEARCH_RESULT':
                # Save the result, and print it
                thread.start_new_thread(self._show_result, (data,))

            elif msg_type == 'DOWNLOAD':
                # Some one wants to download one of its files
                file_path = data['file_path']
                thread.start_new_thread(
                    self._send_file, (incoming_id, file_path))

            elif msg_type == 'YOUR_READ_PEERS':
                # Get the peer list and send them its file list
                thread.start_new_thread(self._ask_peers, (data,))

            elif msg_type == 'YOUR_WRITE_PEERS':
                # Get the peer list and send them its file list
                thread.start_new_thread(self._send_file_list, (data,))

            else:
                print >> self._log_file, 'Unidentified message type {}'.format(msg_type)

    def _auto_get_write_peers(self):
        # time.sleep(1)
        conn = jsocket.Client()
        while True:
            print >> self._log_file, constants.NORMAL_TAG, 'Calling _auto_get_write_peers'
            conn = jsocket.Client()
            conn.connect('localhost', constants.LOGIN_PORT)
            conn.send({
                'type': 'GET_PEERS_WRITE',
                'node_id': self._node_id
            })
            conn.close()
            time.sleep(constants.GET_PEERS_TIMEOUT())

    def _get_read_peers(self):
        conn = jsocket.Client()
        conn.connect('localhost', constants.LOGIN_PORT)
        conn.send({
            'type': 'GET_PEERS_READ',
            'node_id': self._node_id
        })
        conn.close()

    def _print_msg_info(self, data):
        print >> self._log_file, constants.NORMAL_TAG,
        print >> self._log_file, 'Recieved {} from {}.'.format(data['type'], data['node_id'])

    def _make_sure_exits(self, folder):
        try:
            os.makedirs(folder)
        except OSError:
            if not os.path.isdir(folder):
                raise

    def _show_result(self, data):
        self._search_results = data['file_list']
        print 'Search Results'
        for i in xrange(len(self._search_results)):
            print i, self._search_results[i][0], self._search_results[i][1]
        print '$',

    def _send_file(self, node_id, file_path):
        conn = jsocket.Client()
        conn.connect('localhost', node_id)
        with open(file_path, 'rb') as file_to_send:
            for line in file_to_send:
                conn.sendall(line)
        conn.close()

    def _ask_peers(self, data):
        if self._search_string is not None:
            peers = data['peers']
            for p in peers:
                conn = jsocket.Client()
                conn.connect('localhost', p)
                conn.send({
                    'type': 'SEARCH',
                    'node_id': self._node_id,
                    'query': self._search_string
                })
                conn.close()
            self._search_string = None

    def _send_file_list(self, data):
        peers = data['peers']
        print >> self._log_file, constants.NORMAL_TAG, peers
        file_list = []
        for (dir_path, dir_names, file_names) in os.walk(self._shared_folder):
            file_list.extend(file_names)
        print >> self._log_file, constants.NORMAL_TAG, 'File list'
        print >> self._log_file, file_list
        for p in peers:
            try:
                conn = jsocket.Client()
                conn.connect('localhost', p)
                conn.send({
                    'type': 'SHARE_MY_FILES',
                    'node_id': self._node_id,
                    'shared_files': file_list
                })
                conn.close()
            except Exception as e:
                conn.close()
                continue

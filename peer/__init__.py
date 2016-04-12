import threading
import time
import jsocket
import thread
import constants


class peer_node(threading.Thread):
    node_id = None

    def __init__(self, id):
        self.node_id = id
        threading.Thread.__init__(self)
        print 'Creating peer node'
        self.sock = jsocket.Server('localhost', self.node_id)

    def run(self):
        thread.start_new_thread(self.file_invalidator, ())

        sock = jsocket.Client()
        sock.connect('localhost', constants.LOGIN_PORT)
        sock.send({'type': 'I_AM_PEER'})
        sock.close()

        while True:
            conn, = self.sock.accept()
            data = self.sock.recv(conn)
            node_id = data['node_id']
            msg_type = data['type']
            if msg_type == 'ARE_YOU_ALIVE':
                thread.start_new_thread(
                    self.sock.send_and_close,
                    (conn, {'type': 'I_AM_ALIVE'})
                )
            else:
                conn.close()

    def file_list_manager(self, data):
        for f in data.keylist():
            if f.startswith('file'):
                f = data[f]
                self.file_list.insert(f)
                self.file_time = time.time()

    def file_invalidator(self):
        pass

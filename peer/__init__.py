import threading
import time
import jsocket
import thread
import constants
import datetime

class peer_node(threading.Thread):
    node_id = None
    file_list = {}
    file_list_lock = threading.Lock()

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
            conn = self.sock.accept()
            data = self.sock.recv(conn)
            print_msg_info(data)
            recv_node_id = data['node_id']
            msg_type = data['type']
            if msg_type == 'ARE_YOU_ALIVE':
                thread.start_new_thread(
                    self.sock.send_and_close,
                    (conn, {'type': 'I_AM_ALIVE'})
                )
            elif msg_type == "SHARE_MY_FILES":
                # Use a mutex or a lock while accessing critical section file_list of a peer.
                file_names = data['shared_files']
                thread.start_new_thread(add_files, (conn, recv_node_id, file_names))
            elif msg_type == "DELETE_MY_FILES":
                file_names = data['Deleted_files']
                thread.start_new_thread(delete_files, (conn, recv_node_id, file_names))
            else:
                conn.close()

    def add_files(conn, node_id, file_names):
        self.file_list_lock.aquire()
        curr_time = datetime.datetime.now()
        for i in range(len(file_names)):
            self.file_list[node_id + "_" + file_names[i]] = ((node_id, file_names[i], curr_time))
        self.file_list_lock.release()
        msg = {'type': 'FILES_SHARED_ACK', 'node_id' = self.node_id}
        self.sock.send_and_close(conn, msg)

    def delete_files(conn, node_id, file_names):
        self.file_list_lock.aquire()
        for i in range(len(file_names)):
            if (node_id + '_' + file_names[i]) in self.file_list:
                del self.file_list[node_id + '_' + file_names[i]]
        self.file_list_lock.release()
        msg = {'type': 'FILES_DELETED_ACK', 'node_id' = self.node_id}
        self.sock.send_and_close(conn, msg)


    def file_list_manager(self, data):
        for f in data.keylist():
            if f.startswith('file'):
                f = data[f]
                self.file_list.insert(f)
                self.file_time = time.time()

    def file_invalidator(self):
        pass

def print_msg_info(data):
    print 'Recieved {} from {}.'.format(data['type'], data['node_id'])

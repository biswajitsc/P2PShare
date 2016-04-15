import os
import threading
import time
import jsocket
import thread
import constants
import datetime
import operator
import re


class Peer(threading.Thread):

    def __init__(self, id):
        super(Peer, self).__init__()
        self.node_id = id
        self.file_list = {}
        self.file_list_lock = threading.Lock()
        self._log_file = open('log.txt', 'a')
        print >> self._log_file, constants.PEER_TAG, 'Creating peer node'
        self.sock = jsocket.Server('localhost', self.node_id)

    def run(self):
        thread_obj = threading.Thread(target=self.garbage_collection)
        thread_obj.daemon = True
        thread_obj.start()

        sock = jsocket.Client()
        sock.connect('localhost', constants.LOGIN_PORT)
        sock.send({'type': 'I_AM_PEER', 'node_id': self.node_id})
        sock.close()

        while True:
            conn, dummy = self.sock.accept()
            data = self.sock.recv(conn)
            self.print_msg_info(data)
            conn.close()

            recv_node_id = data['node_id']
            msg_type = data['type']

            print >> self._log_file, constants.PEER_TAG, 'Data is: ',
            print >> self._log_file, data

            conn = jsocket.Client()
            conn.connect('localhost', recv_node_id)

            if msg_type == "SHARE_MY_FILES":
                # Use a mutex or a lock while accessing critical section
                # file_list of a peer.
                file_names = data['shared_files']
                thread.start_new_thread(
                    self.add_files, (conn, recv_node_id, file_names))

            # elif msg_type == "DELETE_MY_FILES":
            #     file_names = data['Deleted_files']
            #     thread.start_new_thread(
            #         self.delete_files, (conn, recv_node_id, file_names))

            elif msg_type == "SEARCH":
                query_file_name = data['query']
                thread.start_new_thread(
                    self.search_file_list, (conn, query_file_name, recv_node_id))

            else:
                conn.close()

    def search_file_list(self, conn, query, node_id):
        query_strings = re.findall(r'\w+', query)
        self.file_list_lock.acquire()
        ranked_list = {}
        for name in self.file_list:
            strngs = re.findall(r'\w+', name[1])
            count = 0
            for string in query_strings:
                for strng in strngs:
                    if (string in strng) or (strng in string):
                        count += 1
                        break
            ranked_list[name] = (count * 1.0) / len(query_strings)
        self.file_list_lock.release()
        sorted_tags = sorted(
            ranked_list.items(), key=operator.itemgetter(1), reverse=True)
        sorted_file_list = []
        for i in range(len(sorted_tags)):
            sorted_file_list.append(sorted_tags[i][0])
        msg = {'type': "SEARCH_RESULT", 'node_id': self.node_id, 'file_list': sorted_file_list}
        conn.send(msg)
        conn.close()

    def add_files(self, conn, node_id, file_names):
        self.file_list_lock.acquire()
        curr_time = datetime.datetime.now()
        for i in range(len(file_names)):
            self.file_list[(node_id, file_names[i])] = curr_time
        self.file_list_lock.release()
        print >> self._log_file, constants.PEER_TAG, " : Files Added from " + str(node_id) + "!!"
        self.print_file_table()
        # msg = {'type': 'FILES_SHARED_ACK', 'node_id' : self.node_id}
        # self.sock.send_and_close(conn, msg)
        conn.close()

    def garbage_collection(self):
        while(True):
            time.sleep(constants.GARBAGE_COLLECT_TIMEOUT())
            self.file_list_lock.acquire()
            delete_files = []
            curr_time = datetime.datetime.now()
            
            for index in self.file_list:
                time_difference =  curr_time - self.file_list[index]
                if time_difference.total_seconds() >= constants.FILE_INVALIDATE_TIMEOUT():
                    delete_files.append(index)

            for index in delete_files:
                del self.file_list[index]
            
            print >> self._log_file, constants.PEER_TAG, " : Garbage Collection Performed!!"
            self.file_list_lock.release()
            
            print >> self._log_file, "\n-------------------- Files to be deleted --------------------------\n"
            for index in delete_files:
                print >> self._log_file, "Node Id : ", index[0], "File Name : ", index[1]

            self.print_file_table()

            conn = jsocket.Client()
            conn.connect('localhost', constants.LOGIN_PORT)
            msg = {
                'type': 'I_AM_ALIVE',
                'node_id': self.node_id
            }
            conn.send(msg)
            conn.close()

    def print_file_table(self):
        print >> self._log_file, "\n+++++++++++++++++++++++++++++++++", str(constants.PEER_TAG), ": File Table +++++++++++++++++++++++\n"
        self.file_list_lock.acquire()
        for index in self.file_list:
            print >> self._log_file, "Node Id : ", str(index[0]), " | ", "File Name : ", str(index[1])
        self.file_list_lock.release()


    def print_msg_info(self, data):
        print >> self._log_file, constants.PEER_TAG,
        print >> self._log_file, 'Recieved {} from {}.'.format(data['type'], data['node_id'])

import threading
import time
import jsocket
import thread
import constants
import datetime
import re

class Peer(threading.Thread):

	def __init__(self, id):
		self.node_id = id
		self.file_list = {}
		self.file_list_lock = threading.Lock()
		# threading.Thread.__init__(self)
		super(Peer, self).__init__(self)
		print 'Creating peer node'
		self.sock = jsocket.Server('localhost', self.node_id)

	def run(self):
		# thread.start_new_thread(self.file_invalidator, ())
		thread.start_new_thread(self.garbage_collection, ())

		sock = jsocket.Client()
		sock.connect('localhost', constants.LOGIN_PORT)
		sock.send({'type': 'I_AM_PEER', 'node_id' : self.node_id})
		sock.close()

		while True:
			conn, dummy = self.sock.accept()
			data = self.sock.recv(conn)
			print_msg_info(data)
			conn.close()

			recv_node_id = data['node_id']
			msg_type = data['type']
			
			conn = jsocket.Client()
			conn.connect('localhost', recv_node_id)

			if msg_type == 'ARE_YOU_ALIVE':
				thread.start_new_thread(
					self.sock.send_and_close,
					(conn, {'type': 'I_AM_ALIVE', 'node_id' : self.node_id})
				)
			elif msg_type == "SHARE_MY_FILES":
				# Use a mutex or a lock while accessing critical section file_list of a peer.
				file_names = data['shared_files']
				thread.start_new_thread(add_files, (conn, recv_node_id, file_names))
			elif msg_type == "DELETE_MY_FILES":
				file_names = data['Deleted_files']
				thread.start_new_thread(delete_files, (conn, recv_node_id, file_names))
			elif msg_type == "SEARCH":
				query_file_name = data['query']
				thread.start_new_thread(search_file_list, (conn, query_file_name, recv_node_id))
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
		sorted_tags = sorted(ranked_list.items(), key=operator.itemgetter(1), reverse=True)
		sorted_file_list = []
		for i in range(len(sorted_tags)):
			sorted_file_list.append(sorted_tags[i][0])
		msg = {'type' : "SEARCH_RESULT", 'file_list' : sorted_file_list}
		self.sock.send_and_close(conn, msg)


	def add_files(self, conn, node_id, file_names):
		self.file_list_lock.aquire()
		curr_time = datetime.datetime.now()
		for i in range(len(file_names)):
			self.file_list[(node_id, file_names[i])] = ((node_id, file_names[i], curr_time))
		self.file_list_lock.release()
		# msg = {'type': 'FILES_SHARED_ACK', 'node_id' : self.node_id}
		# self.sock.send_and_close(conn, msg)
		conn.close()

	def delete_files(self, conn, node_id, file_names):
		self.file_list_lock.aquire()
		for i in range(len(file_names)):
			if ((node_id, file_names[i]) in self.file_list):
				del self.file_list[(node_id, file_names[i])]
		self.file_list_lock.release()
		# msg = {'type': 'FILES_DELETED_ACK', 'node_id' : self.node_id}
		# self.sock.send_and_close(conn, msg)
		conn.close()


	def garbage_collection(self):
		prev_time = datetime.datetime.now()
		while(True):
			curr_time = datetime.datetime.now()
			time_elapsed = curr_time - prev_time
			if time_elapsed.total_seconds() < 300:
				continue
			prev_time = curr_time
			self.file_list_lock.aquire()
			delete_files = []
			for index in self.file_list:
				time_difference = self.file_list[index][2] - curr_time
				if curr_time.total_seconds >= 600:
					delete_files.append(index)
			for index in delete_files:
				del self.file_list[index]
			self.file_list_lock.release()

	# def file_list_manager(self, data):
	#     for f in data.keylist():
	#         if f.startswith('file'):
	#             f = data[f]
	#             self.file_list.insert(f)
	#             self.file_time = time.time()

	# def file_invalidator(self):
	#     pass

def print_msg_info(data):
	print 'Recieved {} from {}.'.format(data['type'], data['node_id'])

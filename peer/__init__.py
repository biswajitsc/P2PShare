import threading
from time import sleep


class peer_node(threading.Thread):
    node_id = None
    conn = None

    def __init__(self, id):
        self.node_id = id
        threading.Thread.__init__(self)
        print 'Creating peer node'

    def run(self):
        while True:
            pass
    
    def file_list_manager(self, data):
        for f in data.keylist():
            if f.startswith('file'):
                f = data[f]
                self.file_list.insert(f)
                self.file_time = time.time()

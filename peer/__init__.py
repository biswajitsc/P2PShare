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

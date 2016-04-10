import threading

from time import sleep


class normal_node(threading.Thread):
    node_id = None

    def __init__(self, id):
        self.node_id = id
        threading.Thread.__init__(self)
        print 'Creating normal node'

    def run(self):
        while True:
            try:
                print 'User running'
                sleep(10)
            except Exception as e:
                print e
                return

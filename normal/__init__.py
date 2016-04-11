import threading
import jsocket
import constants

from time import sleep


class normal_node(threading.Thread):
    node_id = None
    conn = None

    def __init__(self, id):
        self.node_id = id
        threading.Thread.__init__(self)
        print 'Creating normal node'
        self.conn = jsocket.Client()

    def run(self):
        while True:
            try:
                print 'User running'
                self.conn.connect('localhost', constants.LOGIN_PORT)
                self.conn.send({
                    'type': 'I_AM_ONLINE',
                    'node_id': self.node_id
                })
                self.conn.close()
                sleep(10)
            except Exception as e:
                print e
                return

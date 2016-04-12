import os
import threading
import jsocket
import constants

class normal_node(threading.Thread):
    node_id = None
    conn = None
    shared_folder = None
    def __init__(self, id):
        self.node_id = id
        threading.Thread.__init__(self)
        print 'Creating normal node'
        self.conn = jsocket.Client()
        shared_folder = 'Data/' + str(node_id)
        print 'Shared folder', shared_folder
        self.conn.connect('localhost', constants.LOGIN_PORT)
        self.conn.send({
                'type': 'I_AM_ONLINE',
                'node_id': self.node_id
            })
        self.conn.close()

    def run(self):
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

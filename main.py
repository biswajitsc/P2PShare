import threading
import normal
import peer
import sys
import server
import time


def main():
    print 'Main starting'
    if len(sys.argv) < 2:
        print '[ERROR] Please provide Node ID'
        exit(0)

    node_id = sys.argv[1]
    node_id = node_id.lower()

    if node_id == 'server':
        server_obj = server.Server()
        server_obj.run()
    else:
        node_id = int(node_id)
        if node_id <= 8000 or node_id > 9000 or node_id % 2 == 1:
            raise Exception('node_id must be an even number between\
                8001 and 9000 inclusive.')

        n_node = normal.NormalNode(node_id)
        n_node.daemon = True
        n_node.start()

        n_node.join()

    print 'Main exiting'


if __name__ == '__main__':
    main()

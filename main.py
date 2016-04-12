import threading
import normal
import peer
import sys
import server


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

        n_node = normal.normal_node(node_id)
        # p_node = peer.peer_node(node_id+1)

        n_node.start()
        # p_node.start()

        n_node.join()
        # p_node.join()

    print 'Main exiting'

if __name__ == '__main__':
    main()

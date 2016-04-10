import threading
import normal
import peer
import sys

def main():
    print 'Main starting',
    node_id = sys.argv[1]
    n_node = normal.normal_node(node_id+'_normal')
    p_node = peer.peer_node(node_id+'_peer')

    n_node.start()
    p_node.start()

    n_node.join()
    p_node.join()
    print 'Main exiting'

if __name__ == '__main__':
    main()

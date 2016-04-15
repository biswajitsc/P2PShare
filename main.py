import threading
import normal
import peer
import sys
import server
import time
import constants
import getip

def main():
    print 'Main starting'
    if len(sys.argv) < 2:
        print '[ERROR] Please provide Node ID'
        exit(0)

    node_id = sys.argv[1]
    node_id = node_id.lower()
    ip = getip.get_lan_ip()

    if node_id == 'server1':
        server_obj = server.Server(
            constants.LOGIN_ADD1, constants.LOGIN_ADD2)
        server_obj.run()
    if node_id == 'server2':
        server_obj = server.Server(
            constants.LOGIN_ADD2, constants.LOGIN_ADD1)
        server_obj.run()
    else:
        node_id = int(node_id)
        if node_id <= 8001 or node_id > 9000 or node_id % 2 == 1:
            raise Exception('node_id must be an even number between\
                8002 and 9000 inclusive.')

        n_node = normal.NormalNode(str(ip)+':'+str(node_id))
        n_node.daemon = True
        n_node.start()

    while True:
        time.sleep(120)

    print 'Main exiting'


if __name__ == '__main__':
    main()

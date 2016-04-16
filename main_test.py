import threading
import normal
import peer
import sys
import server
import time
import constants
import getip
import random


def main(node_id):

    ip = getip.get_lan_ip()

    if node_id <= 8001 or node_id > 9000 or node_id % 2 == 1:
        raise Exception('node_id must be an even number between\
            8002 and 9000 inclusive.')

    n_node = normal.NormalNode(str(ip) + ':' + str(node_id))
    n_node.daemon = True
    n_node.start()

    while True:
        time.sleep(120)
        if random.random() < 0.5:
            exit(1)

    print 'Main exiting'

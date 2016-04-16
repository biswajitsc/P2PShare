import random
import math

LOGIN_ADD1 = '10.145.14.209:8000'
LOGIN_ADD2 = '10.146.24.166:8001'
# LOGIN_ADD1 = 'localhost:8000'
# LOGIN_ADD2 = 'localhost:8001'
# LOGIN_IP1 = 'localhost'
# LOGIN_IP2 = 'localhost'
# LOGIN_PORT1 = 8000
# LOGIN_PORT2 = 8001
MAX_PEERS = 1
SEARCH_WAIT = 5
WRITE_QUORUM = 2
BUFFER_SIZE = 1024


def MAX_OFFLINE_TIME():
    tval = 30
    return tval  # + random.randint(0, tval)


def SELECT_PEER_TIMEOUT():
    tval = 5
    return tval + random.randint(0, tval)


def HEARTBEAT_TIMEOUT():
    tval = 5
    return tval + random.randint(0, tval)


def GET_PEERS_TIMEOUT():
    tval = 7
    return tval + random.randint(0, tval)


def GARBAGE_COLLECT_TIMEOUT():
    tval = 5
    return tval + random.randint(0, tval)


def FILE_INVALIDATE_TIMEOUT():
    tval = 10
    return tval


def GET_PEER_READ_SIZE(num_peers):
    write_quorum = min(2, num_peers)
    return (num_peers - write_quorum + 1)


def GET_PEER_WRITE_SIZE(num_peers):
    return min(WRITE_QUORUM, num_peers)


def MAX_PEERS(num_normal_nodes):
    return min(int(math.sqrt(num_normal_nodes)), 20)

NORMAL_TAG = '[NORMAL]'
PEER_TAG = '[PEER]'
INFO_TAG = '[INFO]'


def SUPER_PEER_TAG(node_id):
    return '[SUPER_PEER {}]'.format(node_id)

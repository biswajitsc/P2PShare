import random
import math

LOGIN_PORT1 = 8000
LOGIN_PORT2 = 8001
MAX_PEERS = 1
WRITE_QUORUM = 2


def MAX_OFFLINE_TIME():
    tval = 10
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
    return (num_peers - WRITE_QUORUM + 1)


def GET_PEER_WRITE_SIZE(num_peers):
    return WRITE_QUORUM


def MAX_PEERS(num_normal_nodes):
    return min(int(math.sqrt(num_normal_nodes)), 20)

NORMAL_TAG = '[NORMAL]'
SUPER_PEER_TAG = '[SUPER_PEER]'
PEER_TAG = '[PEER]'
INFO_TAG = '[INFO]'

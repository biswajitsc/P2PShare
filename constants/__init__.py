import random

LOGIN_PORT = 8000
MAX_PEERS = 1


def MAX_OFFLINE_TIME():
    tval = 5
    return tval + random.randint(1, tval)


def SELECT_PEER_TIMEOUT():
    tval = 15
    return tval + random.randint(1, tval)


def HEARTBEAT_TIMEOUT():
    tval = 15
    return tval + random.randint(1, tval)


def GET_PEERS_TIMEOUT():
    tval = 5
    return tval + random.randint(1, tval)


def GARBAGE_COLLECT_TIMEOUT():
    tval = 20
    return tval + random.randint(1, tval)


def FILE_INVALIDATE_TIMEOUT():
    tval = 7
    return tval

NORMAL_TAG = '[NORMAL]'
SUPER_PEER_TAG = '[SUPER_PEER]'
PEER_TAG = '[PEER]'
INFO_TAG = '[INFO]'

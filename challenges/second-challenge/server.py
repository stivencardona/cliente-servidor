import zmq
from zhelpers import socket_set_hwm, zpipe

CHUNK_SIZE=250000

ctx = zmq.Context()

file = open("testdata", "rb")

router = ctx.socket(zmq.ROUTER)

socket_set_hwm(router, 0)
router.bind("tcp://*:6000")

while True:
    try:
        identity, command = router.recv_multipart()
    except zmq.ZMQError as e:
        if e.errno == zmq.ETERM:
            print(e.errno)
        else:
            raise

    assert command == b"fetch"
    while True:
        data = file.read(CHUNK_SIZE)
        router.send_multipart([identity, data])
        if not data:
            break
ctx.term()
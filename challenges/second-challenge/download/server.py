import zmq
import hashlib

CHUNK_SIZE = 250000

ctx = zmq.Context()

file = open("testdata", "rb")

router = ctx.socket(zmq.ROUTER)

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
    h = hashlib.sha256()
    while True:
        data = file.read(CHUNK_SIZE)
        h.update(data)
        router.send_multipart([identity, data, h.digest()])
        if not data:
            break
ctx.term()

import zmq
import hashlib

CHUNK_SIZE = 250000

ctx = zmq.Context()

router = ctx.socket(zmq.ROUTER)
router.bind("tcp://*:6000")


def download():
    file = open("storage-server/testdata", "rb")
    h = hashlib.sha256()
    chunks = 0
    size = 0
    total = 0
    while True:
        data = file.read(CHUNK_SIZE)
        h.update(data)
        chunks += 1
        size = len(data)
        total += size
        print("%i chunks send, %i bytes" % (chunks, total))
        router.send_multipart([identity, data, h.digest()])
        if not data:
            break
    print("Complete process")

def upload():
    chunks = 0
    total = 0
    outfile = open("storage-server/testout", "wb")
    check = hashlib.sha256()
    while True:
        try:
            identity, chunk, h = router.recv_multipart()
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                print(e.errno)   # shutting down, quit
            else:
                raise
        chunks += 1
        size = len(chunk)
        total += size
        if size == 0:
            print("Download complete")
            break
        else:
            check.update(chunk)
            if check.digest() != h:
                break
            outfile.write(chunk)
    print("%i chunks received, %i bytes" % (chunks, total))

print("Listening on port 6000")

while True:
    try:
        identity, command = router.recv_multipart()
    except zmq.ZMQError as e:
        if e.errno == zmq.ETERM:
            print(e.errno)
        else:
            raise
    print("Client connected")
    assert command == b"download" or command == b"upload"
    if command == b"download":
        download()
    else:
        upload()

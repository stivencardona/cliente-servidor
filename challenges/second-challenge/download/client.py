import zmq
import hashlib
from zhelpers import socket_set_hwm, zpipe

ctx = zmq.Context()
a, pipe = zpipe(ctx)

dealer = ctx.socket(zmq.DEALER)
dealer.connect("tcp://127.0.0.1:6000")
dealer.send(b"fetch")

total = 0       # Total bytes received
chunks = 0      # Total chunks received
outfile = open("testout", "wb")
check = hashlib.sha256()

while True:
    try:
        chunk, h = dealer.recv_multipart()
    except zmq.ZMQError as e:
        if e.errno == zmq.ETERM:
            print(e.errno)   # shutting down, quit
        else:
            raise
    chunks += 1
    size = len(chunk)
    total += size
    if size == 0:
        break   # whole file received
    else:
        check.update(chunk)
        if check.digest() != h:
            break
        outfile.write(chunk)
print("%i chunks received, %i bytes" % (chunks, total))
pipe.send(b"OK")
del a, pipe
ctx.term()

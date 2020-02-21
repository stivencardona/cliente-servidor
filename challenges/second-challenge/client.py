import zmq
import hashlib

CHUNK_SIZE = 25000

ctx = zmq.Context()

dealer = ctx.socket(zmq.DEALER)
dealer.connect("tcp://127.0.0.1:6000")

def download():
	dealer.send(b"download")
	total = 0       # Total bytes received
	chunks = 0      # Total chunks received
	outfile = open("storage-client/testout", "wb")
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

def upload():
	dealer.send(b"upload")
	file = open("storage-client/testdata", "rb")
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
		dealer.send_multipart([data, h.digest()])
		if not data:
			break
	print("Upload complete")

while True:
	command = input()
	if command == "download":
		download()
	else:
		upload()

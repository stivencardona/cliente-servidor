import zmq
import json
import hashlib

class Client:
	def __init__(self, CHUNKSIZE = 2097152):
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.REQ)
		self.CHUNKSIZE = CHUNKSIZE
		self.segment_list = []
	
	def get_hash(self, data):
		return hashlib.sha256(data)

	def set_proxy(self, proxy_ip = "localhost",proxy_port = 5556):
		self.proxy_ip = proxy_ip
		self.proxy_port = proxy_port

	def download(self):
		print("Something")

	def send_segment(self, data, server_ip, server_port):
		addr = "tcp://{}:{}".format(server_ip, server_port)
		self.socket.connect(addr)
		print("Connect to {}".format(addr))
		h = self.get_hash(data)
		self.socket.send_multipart([b"upload", data, h.digest()])
		message = self.socket.recv()
		if message == b"ok":
			self.segment_list.append(addr)
		self.socket.disconnect(addr)
		return h.hexdigest()

	def upload(self, filename):
		addr = "tcp://{}:{}".format(self.proxy_ip , self.proxy_port)
		self.socket.connect(addr)
		self.socket.send(b"list")
		server_list = json.loads(self.socket.recv().decode('utf8'))
		self.socket.disconnect(addr)
		path = "storage-client/" + filename
		self.segment_list = []
		with open(path,"rb") as f:
			chunk = 0
			total = 0
			data = f.read(self.CHUNKSIZE)
			sz = len(server_list)
			while data:
				idx = chunk % sz
				self.send_segment(data, server_list[idx][0], server_list[idx][1])
				chunk += 1
				total += len(data)
				print("{} chunks send, {} bytes".format(chunk, total))
				data = f.read(self.CHUNKSIZE)
		self.socket.connect(addr)
		self.socket.send(b"upload")
		self.socket.recv()
		self.socket.send(json.dumps([filename, self.segment_list]).encode('utf8'))
		self.socket.recv()
		self.socket.disconnect(addr)
		print("Upload complete")

client = Client(10485760)
client.set_proxy()
client.upload("testfile")

# context = zmq.Context()

# #  Socket to talk to server
# print("Connecting to hello world server…")
# socket = context.socket(zmq.REQ)
# socket.connect("tcp://localhost:5555")

# #  Do 10 requests, waiting each time for a response
# file = open("testdata", "rb")
# data = file.read()
# h = hashlib.sha256()
# h.update(data)

# # socket.send_multipart([b"upload", data, h.digest()])

# socket.send_multipart([b"download", b"713cfd41e074775ad4a97e5343cdee05ba9dc654a265427e0d73e44765730a7f"])

# data, check = socket.recv_multipart()
# name = hashlib.sha256()
# name.update(data)
# file = open("storage-client/" + name.hexdigest() , "wb")
# file.write(data)
# # Testing proxy list 

# #  Get the reply.
# # message = socket.recv()
# # result = json.loads(message.decode('utf8')) 
# # print("Received reply %s" % (message))


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
		self.socket.send_multipart([b"list"])
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
		self.socket.send_multipart([b"upload", json.dumps([filename, self.segment_list]).encode('utf8')])
		self.socket.disconnect(addr)
		print("Upload complete")

client = Client(10485760)
client.set_proxy()
client.upload("testfile")
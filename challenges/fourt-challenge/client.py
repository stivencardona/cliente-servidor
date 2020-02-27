import zmq
import json
import hashlib

class Client:
	def __init__(self, CHUNKSIZE = 2097152):
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.REQ)
		self.CHUNKSIZE = CHUNKSIZE
		self.segment_list = []
		self.dir = "storage-client/"
	
	def get_hash(self, data):
		return hashlib.sha256(data)

	def set_proxy(self, proxy_ip = "localhost",proxy_port = 5556):
		self.addr_proxy = "tcp://{}:{}".format(proxy_ip , proxy_port)

	def recv_segment(self, server_ip, filename):
		self.socket.connect(server_ip)
		self.socket.send_multipart([b"download", filename.encode('utf8')])
		data, h = self.socket.recv_multipart()
		check = self.get_hash(data)
		if check.digest() == h:
			self.socket.disconnect(server_ip)
			return data
		else:
			self.recv_segment(server_ip, filename)

	def download(self, filename): 
		self.socket.connect(self.addr_proxy)
		self.socket.send_multipart([b"file", filename.encode('utf8')])
		download_list = json.loads(self.socket.recv().decode('utf8'))
		self.socket.disconnect(self.addr_proxy)
		path = self.dir + filename
		with open(path, "wb") as f:
			for server in download_list:
				data = self.recv_segment(server[0], server[1])
				f.write(data)
				print("Download {}".format(self.get_hash(data).hexdigest()))
		print("Download complete")

	def send_segment(self, data, server_ip, server_port):
		addr = "tcp://{}:{}".format(server_ip, server_port)
		self.socket.connect(addr)
		print("Connect to {}".format(addr))
		h = self.get_hash(data)
		self.socket.send_multipart([b"upload", data, h.digest()])
		message = self.socket.recv()
		if message == b"ok":
			self.segment_list.append([addr, h.hexdigest()])
		self.socket.disconnect(addr)

	def upload(self, filename):
		self.socket.connect(self.addr_proxy)
		self.socket.send_multipart([b"list"])
		server_list = json.loads(self.socket.recv().decode('utf8'))
		self.socket.disconnect(self.addr_proxy)
		path = self.dir + filename
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
		self.socket.connect(self.addr_proxy)
		self.socket.send_multipart([b"upload", json.dumps([filename, self.segment_list]).encode('utf8')])
		self.socket.recv()
		self.socket.disconnect(self.addr_proxy)
		print("Upload complete")

client = Client(10485760)
client.set_proxy()
client.upload("testfile")
client.download("testfile")
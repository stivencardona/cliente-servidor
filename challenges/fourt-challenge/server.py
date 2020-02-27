import zmq
import socket
import hashlib
import sys

class Server:
	def __init__(self, ip = "localhost", port = 5555):
		self.context = zmq.Context()
		self.socketRep = self.context.socket(zmq.REP)
		self.socketReq = self.context.socket(zmq.REQ)
		self.port = port
		self.ip = ip
		self.dir = "storage-server-{}-{}/".format(self.ip,self.port)
		self.socketRep.bind("tcp://*:{}".format(self.port))
	
	def register(self, proxy_ip = "localhost",proxy_port = 5556):
		self.socketReq.connect("tcp://{}:{}".format(proxy_ip, proxy_port))
		self.socketReq.send_multipart([b"register", self.ip.encode('utf8'), "{}".format(self.port).encode('utf8')])
		if self.socketReq.recv() == b"ok":
			print("Register success")
		self.socketReq.close()
	
	def upload(self, data, h):
		print("Upload process")
		check = hashlib.sha256()
		check.update(data)
		if check.digest() != h:
			print("File corrupt")
		path = self.dir + check.hexdigest()
		with open(path, "wb") as f:
			f.write(data)
			self.socketRep.send(b"ok")
		print("Store file {}".format(check.hexdigest()))


	def download(self, filename):
		h = hashlib.sha256()
		with open(self.dir + filename, "rb") as f:
			data = f.read()
			h.update(data)
			self.socketRep.send_multipart([data, h.digest()])
		print("Download process")

	def up(self, proxy_ip = "localhost",proxy_port = 5556):
		print("Server listenning on {}".format(self.port))
		self.register(proxy_ip, proxy_port)
		while True:
			arg = self.socketRep.recv_multipart()
			command = arg[0]
			if command == b"download":
				filename = arg[1].decode('utf8')
				self.download(filename)
			if command == b"upload":
				data = arg[1]
				h = arg[2]
				self.upload(data, h) 

name, ip, port = sys.argv
server = Server(ip,port)
proxy_ip = input()
proxy_port = input()
server.up(proxy_ip, proxy_port)
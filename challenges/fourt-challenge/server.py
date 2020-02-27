import zmq
import socket
import hashlib

class Server:
	def __init__(self, port = 5555):
		self.context = zmq.Context()
		self.socketRep = self.context.socket(zmq.REP)
		self.socketReq = self.context.socket(zmq.REQ)
		self.port = port
		self.socketRep.bind("tcp://*:{}".format(self.port))
	
	def register(self, proxy_ip = "localhost",proxy_port = 5556, sever_ip = "localhost"):
		self.socketReq.connect("tcp://{}:{}".format(proxy_ip, proxy_port))
		self.socketReq.send_multipart([b"register", sever_ip.encode('utf8'), "{}".format(self.port).encode('utf8')])
		if self.socketReq.recv() == b"ok":
			print("Register success")
		self.socketReq.close()
	
	def upload(self, data, h):
		print("Upload process")
		check = hashlib.sha256()
		check.update(data)
		if check.digest() != h:
			print("File corrupt")
		filename = "storage-server/" + check.hexdigest()
		outfile = open(filename, "wb")
		outfile.write(data)
		self.socketRep.send(b"ok")
		print("Store file {}".format(check.hexdigest()))


	def download(self, filename):
		print("Download process")
		h = hashlib.sha256()
		file = open("storage-server/" + filename, "rb")
		data = file.read()
		h.update(data)
		self.socketRep.send_multipart([data, h.digest()])

	def up(self):
		print("Server listenning on %i" % self.port)
		self.register()
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

port = int(input())
server = Server(port)
server.up()
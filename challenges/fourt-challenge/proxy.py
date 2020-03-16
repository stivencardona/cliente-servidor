import zmq
import json
import sys

class Proxy:
	def __init__(self, port):
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.REP)
		self.port = port
		self.socket.bind("tcp://*:{}".format(self.port))
		self.server_list = []
		self.list_files = {}
	
	def get_file_list(self, filename):
		self.socket.send(json.dumps(self.list_files[filename]).encode('utf8'))

	def get_files(self):
		self.socket.send(self.list_files.keys())

	def store_file(self, data):
		data = json.loads(data.decode('utf8'))
		self.list_files[data[0]] = data[1]
		self.socket.send(b"ok")
		print(self.list_files.keys())

	def store_server(self, data):
		print("Server store")
		self.server_list.append([data[0].decode('utf8'), data[1].decode('utf8')])
		self.socket.send(b"ok")
	
	def get_server_list(self):
		self.socket.send(json.dumps(self.server_list).encode('utf8')) 

	def up(self):
		print("Server listenning on {}".format(self.port))
		while True:
			arg = self.socket.recv_multipart()
			if arg[0] == b"register":
				self.store_server([arg[1], arg[2]])
			if arg[0] == b"list":
				self.get_server_list()
			if arg[0] == b"upload":
				self.store_file(arg[1])
			if arg[0] == b"file":
				self.get_file_list(arg[1].decode('utf8'))
			if arg[0] == b"files":
				self.get_files()

name, port = sys.argv
proxy = Proxy(port)
proxy.up()
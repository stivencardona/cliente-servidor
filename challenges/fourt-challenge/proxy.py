import zmq
import json

class Proxy:
	def __init__(self, port):
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.REP)
		self.port = port
		self.socket.bind("tcp://*:%i" % self.port)
		self.server_list = []
		self.commands = {
			b"register": self.store_server,
			b"list": self.get_server_list,
			b"upload": self.store_file,
			b"file": self.get_file
		}
		self.list_files = {}
	
	def get_file(self, filename):
		self.socket.send(json.dumps(self.list_files[filename]))

	def store_file(self):
		self.socket.send(b"ok")
		data = json.loads(self.socket.recv().decode('utf8'))
		self.list_files[data[0]] = data[1]
		self.socket.send(b"ok")
		self.get_file()

	def store_server(self):
		print("Register server")
		self.socket.send(b"ok")
		data = self.socket.recv_multipart()
		data[0] = data[0].decode('utf8')
		data[1] = data[1].decode('utf8')
		self.server_list.append(data)
		self.socket.send(b"ok")
	
	def get_server_list(self):
		self.socket.send(json.dumps(self.server_list).encode('utf8')) 

	def up(self):
		print("Server listenning on {}".format(self.port))
		while True:
			command = self.socket.recv()
			self.commands[command]()

proxy = Proxy(5556)
proxy.up()
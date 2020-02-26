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
			b"upload": self.store_file
		}
		self.list_files = {}
	
	def store_file(self):
		print("Something")

	def store_server(self):
		print("Register server")
		self.socket.send(b"ok")
		data = self.socket.recv_multipart()
		data[0] = data[0].decode('utf8')
		data[1] = data[1].decode('utf8')
		self.server_list.append(data)
		self.socket.send(b"ok")
	
	def get_server_list(self):
		self.socket.send(bytes(json.dumps(self.server_list), 'utf8')) 

	def up(self):
		print("Server listenning on %i" % self.port)
		while True:
			command = self.socket.recv()
			self.commands[command]()

proxy = Proxy(5556)
proxy.up()
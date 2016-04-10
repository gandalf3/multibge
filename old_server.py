#!/usr/bin/env python3
# this script provides a basic echo server capable of multiple connections at once

import threading
from queue import Queue
import socket
import uuid

port = 32453

class Server():
	def __init__(self, port):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.bind(('localhost', port))
		self.socket.listen(5)
		
		self.connected_clients = []

		self.lock = threading.Lock()
		self.max_threads = 512 # maximum number of open connections at one time
		self.open_threads = 0
		
		self.incoming_connections = Queue()

	def handle_connection(self, conn):
		
		myuuid = uuid.uuid4()
		conn.sendall('CONNECT:{}'.format(myuuid).encode())
		self.connected_clients.append({"conn": conn, "uuid": myuuid })
		
		try:
			while True:
				data = conn.recv(1024)
				if data:
					with self.lock:
						print("sending data")
						conn.sendall(data)
				else:
					break
		finally:
			conn.close()
			
	def listen(self):
		while True:
			(conn, address) = self.socket.accept()
			
			if self.open_threads < self.max_threads:
				t = threading.Thread(target = lambda: self.handle_connection(conn))
				t.daemon = True
				t.start()
			else:
				self.incoming_connections.put(conn)
				
		self.incoming_connections.join()
		
if __name__ == "__main__":
	server = Server(port)
	server.listen()

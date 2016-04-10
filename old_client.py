import bpy
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 43847
sock.connect(('localhost', port))

def listen(cont):
    own = cont.owner
    print(sock.recv(1024))
    
    
def send_position(cont):
    own = cont.owner
    data = str(own.worldPosition).encode()
    sock.send(data)
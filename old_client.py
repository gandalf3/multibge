import bge
import uuid
import pickle
import socket
from mathutils import Matrix

port = 32453

class Client():
    
    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('localhost', port))
        self.sock.setblocking(0)
        self.port = port
        self.uuid = uuid.uuid4()
        
        self.other_clients = []        
        
        self.send_data(pickle.dumps(
            {
            "action": "CONNECT",
            "uuid": self.uuid,
            }))
        
            
    def listen(self):

        data = None
        try:
            data = sock.recv(1024)
        except:
            pass
        
        if data:
            unpickled_data = pickle.loads(data)
            print('Data received: {!r}'.format(unpickled_data))

            sender_uuid = unpickled_data['uuid']

            if unpickled_data['action'] == 'UPDATE':
                prop = unpickled_data['property']
                val = unpickled_data['value']
                type = unpickled_data['value_type']
                
                if type == "Matrix":
                    val = Matrix(val)
                
                for other_client in other_clients:
                    if other_client.uuid == sender_uuid:
                        other_client.object[prop] = val
                
            if unpickled_data['action'] == 'CONNECT':
                object = bge.logic.getCurrentScene().addObject('RemoteSuzanne')
                self.other_clients.append({"uuid": uuid, "object": object})
    
    
    def send_data(self, data):
        self.sock.send(data)


def pickle_prep(m):
    # construct a pure python list representation of an iterable thingy (matrix, vector, etc)
    
    list_representation = []
    if hasattr(m, '__len__'):
        for elem in m:
            list_representation.append(pickle_prep(elem))
        print(list_representation)
        return list_representation
    else:
        return m    

def main(cont):
    own = cont.owner
    
    if "client_init" not in own:
        client = Client(port)
        own["client_init"] = True
    
    client.listen()
    client.send_data(pickle.dumps(
            {
            "action": "UPDATE",
            "uuid": client.uuid,
            "property": "worldTransform",
            "value": pickle_prep(own.worldTransform.copy()),
            "value_type": "Matrix",
            }))
#!/usr/bin/env python3

import asyncio
import pickle
import uuid
import bge
from mathutils import Matrix

port = 9999

def compose_message(message, recipient="CLIENT"):
    """
    Take an object of the form {"action": "", "uuid"} and pickle it.
    Also add timestamp
    """
    
    #message.append("timestamp": bge.logic.getFrameTime())
    
#    if recipient != "client":
#        return recipient + pickle.dumps(message)
#    else:
    
    return pickle.dumps(message)
    
    
def server_greeting():
    greeting = compose_message(
    {
        "recipient": "SERVER",
        "action": "CONNECT"
    }
    )
    

class ClientProtocol(asyncio.Protocol):
    def __init__(self, loop):
        self.loop = loop
        self.conn = None
        self.uuid = uuid.uuid4()
        self.other_clients = []
        
    def connection_made(self, transport):
        print("Connected to server")
        
        m = compose_message(
        {
            "action": "CONNECT",
            "uuid": self.uuid,
        })
        
        transport.write(m)
        
        self.conn = transport
        
    # @asyncio.coroutine
    # def send_message(self, data):
    #     self.conn.write(data)

    def data_received(self, data):
        unpickled_data = pickle.loads(data)
        #print('Data received: {!r}'.format(unpickled_data))

        sender_uuid = unpickled_data['uuid']

        if unpickled_data['action'] == 'UPDATE':
            prop = unpickled_data['property']
            val = unpickled_data['value']
            type = unpickled_data['value_type']
            
            if type == "Matrix":
                (loc, rot, scale) = Matrix(val).decompose()
            
            #print("other clients", other_clients)
            for other_client in self.other_clients:
                if other_client["uuid"] == sender_uuid:
                    #other_client["object"][prop] = Matrix(val)
                    other_client["object"].worldPosition = loc
                    other_client["object"].worldOrientation = rot
                    other_client["object"].worldScale = scale
            
        if unpickled_data['action'] == 'CONNECT':

            # say hi to newcomers, but ignore greetings from clients we already know about
            # this ought to be done on the server really, but for now just make it work(tm)
            if any(client['uuid'] == sender_uuid for client in self.other_clients):
                print(sender_uuid, "has reconnected")
                pass
            else:
                object = bge.logic.getCurrentScene().addObject('RemoteSuzanne')
                self.other_clients.append({"uuid": sender_uuid, "object": object})
                print("greetings", sender_uuid)
                self.conn.write(pickle.dumps(
                    {
                    "action": "CONNECT",
                    "uuid": self.uuid,
                    }))


    def connection_lost(self, exc):
        print('The server closed the connection')
        print('Stop the event loop')
        self.loop.stop()
        
        
def pickle_prep(m):
    # construct a pure python list representation of an iterable thingy (matrix, vector, etc)
    
    list_representation = []
    if hasattr(m, '__len__'):
        for elem in m:
            list_representation.append(pickle_prep(elem))
        return list_representation
    else:
        return m
        

def main(cont):
    own = cont.owner
    
    if "client_init" not in own:
        own.loop = asyncio.get_event_loop()
        coro = own.loop.create_connection(lambda: ClientProtocol(own.loop), '127.0.0.1', port)
        #task = asyncio.Task(coro)
        
        own.transport, own.protocol = own.loop.run_until_complete(coro)

        own['client_init'] = True
        
    own.loop.stop()
    own.loop.run_forever()
    #print(dir(own))
    
    #if onwtransport:
    own.transport.write(compose_message(
        {
        "action": "UPDATE",
        "uuid": own.protocol.uuid,
        "property": "worldTransform",
        "value": pickle_prep(own.worldTransform.copy()),
        "value_type": "Matrix",
        }))

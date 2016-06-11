#!/usr/bin/env python3

import asyncio
import pickle
import uuid
import bge
from mathutils import Matrix

port = 9999


class multibgeClientProtocol(asyncio.Protocol):
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
        
        
class multibgeClient(bge.types.GameObject):
    def __init__(self, own):
        # setup asyncio loop
        self.loop = asyncio.get_event_loop()
        
        self.protocol = None
        self.transport = None
        
        self.attributes = []
        self.objects = []
    
    def connect(self, address, port):
        coro = own.loop.create_connection(lambda: multibgeClientProtocol(own.loop), address, port)
        self.transport, self.protocol = own.loop.run_until_complete(coro)

    def sync(self):
        for attribute in attributes:
            self.transport.write(compose_message({
                "action": "UPDATE",
                "uuid": own.protocol.uuid,
                "property": "worldTransform",
                "value": pickle_prep(own.worldTransform.copy()),
                "value_type": "Matrix",
                }))
        
    def main(self):
        # run asyncio loop without blocking game loop
        own.loop.stop()
        own.loop.run_forever()
        

def main(cont):
    own = cont.owner
    
    if "client_init" not in own:
        ownclient = multibgeClient(own)

        own['client_init'] = True
        
    
    
    #if own.transport:
    own

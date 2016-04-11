#!/usr/bin/env python3

import asyncio
import pickle
import uuid
import bge
from mathutils import Matrix

port = 9999

other_clients = []
ownuuid = uuid.uuid4()
conn = None

class ClientProtocol(asyncio.Protocol):
    def __init__(self, loop):
        self.loop = loop

    def connection_made(self, transport):
        global conn
        transport.write(pickle.dumps(
            {
            "action": "CONNECT",
            "uuid": ownuuid,
            }))
        print("Connected to server")
        print("storing connection")
        conn = transport

    def data_received(self, data):
        global other_clients, conn
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
            for other_client in other_clients:
                if other_client["uuid"] == sender_uuid:
                    #other_client["object"][prop] = Matrix(val)
                    other_client["object"].worldPosition = loc
                    other_client["object"].worldOrientation = rot
                    other_client["object"].worldScale = scale
            
        if unpickled_data['action'] == 'CONNECT':

            # say hi to newcomers, but ignore greetings from clients we already know about
            # this ought to be done on the server really, but for now just make it work(tm)
            if any(client['uuid'] == sender_uuid for client in other_clients):
                print(sender_uuid, "has reconnected")
                pass
            else:
                object = bge.logic.getCurrentScene().addObject('RemoteSuzanne')
                other_clients.append({"uuid": sender_uuid, "object": object})
                print("greetings", sender_uuid)
                conn.write(pickle.dumps(
                    {
                    "action": "CONNECT",
                    "uuid": ownuuid,
                    }))


    def connection_lost(self, exc):
        print('The server closed the connection')
        print('Stop the event loop')
        self.loop.stop()
        
        
loop = asyncio.get_event_loop()
coro = loop.create_connection(lambda: ClientProtocol(loop), '127.0.0.1', port)
task = asyncio.Task(coro)

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
    global conn
    own = cont.owner
    
    loop.stop()
    loop.run_forever()
    
    if conn:
        conn.write(pickle.dumps(
            {
            "action": "UPDATE",
            "uuid": ownuuid,
            "property": "worldTransform",
            "value": pickle_prep(own.worldTransform.copy()),
            "value_type": "Matrix",
            }))
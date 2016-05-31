#!/usr/bin/env python3

import pickle
import asyncio
import uuid

port = 9999

connected_clients = []

class ServerProtocol(asyncio.Protocol):
    
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport
        connected_clients.append(self)

    def data_received(self, data):
        message = pickle.loads(data)
        
        print('Data received: {!r}'.format(message))
        
        #if message['recipient'] and message['recipient'] == 'SERVER':
        #    if message['action'] == 'CONNECT':
                
        
        
        
        print('Send: {!r}'.format(message))
        for client in connected_clients:
            if client != self:
                client.transport.write(data)
                
    #def connection_lost(self):

loop = asyncio.get_event_loop()
# Each client connection will create a new protocol instance
coro = loop.create_server(ServerProtocol, '127.0.0.1', port)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()

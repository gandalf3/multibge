#!/usr/bin/env python3

import asyncio

connected_clients = [];

class EchoServerProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport, addr):
        print(addr)
        #connected_clients.append(self)
        self.transport = transport
        
    def send(self, message):
        self.transport.write(message.encode())

    def datagram_received(self, data, addr):
        message = data.decode()
        print('Received %r from %s' % (message, addr))
        for client in connected_clients:
            # client.send(message)
            # if client is not self:
            print('Send %r to %s' % (message, addr))

loop = asyncio.get_event_loop()
print("Starting UDP server")
# One protocol instance will be created to serve all client requests
listen = loop.create_datagram_endpoint(
    EchoServerProtocol, local_addr=('127.0.0.1', 9999))
transport, protocol = loop.run_until_complete(listen)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

transport.close()
loop.close()

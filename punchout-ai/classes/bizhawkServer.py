import socket
import sys
import time
import json
import threading


class Payload(object):
    def __init__(self, j):
            self.__dict__ = json.loads(j)


class BizHawkServer(threading.Thread):
    template = '{"p1":{"Up":%s,"Down":%s,"Left":%s,"Right":%s,"Start":false,"Select":false,"B":%s,"A":%s},"p2":{},"type":"%s","savegamepath":"c:\\\\users\\\\vidal\\\\Desktop\\\\punchOut.state"}'

    publicState = None
    ready = False
    def __init__(self):
        threading.Thread.__init__(self)
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = ('localhost', 9999)
        print('starting up on %s port %s' % server_address)
        self.sock.bind(server_address)

        # Listen for incoming connections
        self.sock.listen(1)

    def run(self):
        # Wait for a connection
        state=None
        print('waiting for a connection')
        self.ready = True
        while True:
            connection, client_address = self.sock.accept()
            try:
                print('connection from %s' % client_address[0])
                data = connection.recv(1024)
                if data:
                    state=Payload(data.decode())
                    return state
            finally:
                # Clean up the connection
                print('closing the connection')
                #connection.close()
                self.publicState = state

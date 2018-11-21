import socket
import sys
import time
import json
import threading


class Payload(object):
    def __init__(self, j):
            self.__dict__ = json.loads(j)

#class BizHawkServer():
class BizHawkServer(threading.Thread):
    template = '{"p1":{"Up":%s,"Down":%s,"Left":%s,"Right":%s,"Start":false,"Select":false,"B":%s,"A":%s},"p2":{},"type":"%s","savegamepath":"c:\\\\users\\\\user\\\\Desktop\\\\punchOut\\\\punchOut4.state"}'

    publicState = None
    ready = False
    def __init__(self):
        threading.Thread.__init__(self)
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = ('localhost', 9999)
        #print('starting up on %s port %s' % server_address)
        self.sock.bind(server_address)

        # Listen for incoming connections
        self.sock.listen(10)

    def listenToClient(self, client, address):
        while True:
            data = client.recv(1024)
            if data:
                state=Payload(data.decode())
                self.publicState = state
            else:
                #print('Client disconnected')
                break

    def run(self):
        # Wait for a connection
        #print('waiting for a connection')
        self.ready = True
        while True:
            client, address = self.sock.accept()
            #print('connection from %s' % address[0])
            threading.Thread(target = self.listenToClient,args = (client,address)).start()


# if __name__ == "__main__":
#     program = BizHawkServer()
#     program.run()


import socket
import sys
import time
import json
import threading

class Payload(object):
    def __init__(self, j):
            self.__dict__ = json.loads(j)


class BizHawkClient():
    template = '{"p1":{"Up":%s,"Down":%s,"Left":%s,"Right":%s,"Start":false,"Select":false,"B":%s,"A":%s},"p2":{},"type":"%s","savegamepath":"c:\\\\users\\\\vidal\\\\Desktop\\\\punchOut.state"}'

    server_address = None
    hit = False
    healthP1 = 100
    healthP2 = 100
    sock = None
    buttons = None

    def __init__(self):
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        self.server_address = ('localhost', 9998)

    def _SendCommandToEmulator(self, command: str)->str:
        formattedTemplate = self.template % (
            self.buttons['up'], self.buttons['down'], self.buttons['left'], self.buttons['right'], self.buttons['a'], self.buttons['b'], command)
        return formattedTemplate

    def Send(self, command: str):
        # Wait for a connection
        print('sending command: %s' % command)
        self.sock.connect(self.server_address)
        if(command != None):
            msg = self._SendCommandToEmulator(command)
            self.sock.sendall(msg.encode('utf-8'))
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

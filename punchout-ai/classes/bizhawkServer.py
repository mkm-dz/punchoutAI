import socket
import sys
import time
import json
import threading
from classes.runner import RunWrapper


class Payload(object):
    def __init__(self, j):
            self.__dict__ = json.loads(j)


class BizHawkServer(threading.Thread):
    template = '{"p1":{"Up":%s,"Down":%s,"Left":%s,"Right":%s,"Start":false,"Select":false,"B":%s,"A":%s},"p2":{},"type":"%s","savegamepath":"c:\\\\users\\\\vidal\\\\Desktop\\\\punchOut.state"}'

    hit = False
    healthP1 = 100
    healthP2 = 100
    sock = None
    commandInQueue = None
    buttons = None
    runner = None
    frameCounter = 0
    resendCommand = False
    msg = None
    commandSent = False
    publicState=None

    def __init__(self, runner: RunWrapper):
        threading.Thread.__init__(self)
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Setting runner
        self.runner = runner
        # Bind the socket to the port
        server_address = ('localhost', 9999)
        print('starting up on %s port %s' % server_address)
        self.sock.bind(server_address)

        # Listen for incoming connections
        self.sock.listen(1)

    def SendIdle(self) -> str:
        formattedTemplate = self.template % (
            False, False, False, False, False, False, 'processing')
        return formattedTemplate

    def SendCommandToEmulator(self, repeat)->str:
        formattedTemplate = self.template % (
        self.buttons['up'], self.buttons['down'], self.buttons['left'], self.buttons['right'], self.buttons['a'], self.buttons['b'], self.commandInQueue)
        self.commandSent = True
        if(repeat==True):
            self.resendCommand=True
        return formattedTemplate

    def ProcessCommand(self,object):
        # deltaHealth = self.healthP1-deserializedObject.p1.health
        # if deltaHealth > 0:
        #     self.healthP1=self.healthP1-deltaHealth
        #     self.hit=True
        # self.runner.SendData()
        tempHolder = self.commandInQueue
        if(tempHolder == 'GetState'):
            self.publicState=object
            return self.msg
        elif(tempHolder =='reset'):
            return self.SendCommandToEmulator(False)
        elif(tempHolder == 'buttons'):
            return self.SendCommandToEmulator(True)

    def run(self):
        # Wait for a connection
        print('waiting for a connection')
        connection, client_address = self.sock.accept()
        msg = None
        try:
            print('connection from %s' % client_address[0])
            while True:
                data = connection.recv(1024).decode()
                if data:
                    if(self.resendCommand == True):
                        self.frameCounter += 1
                        if(self.frameCounter == 5):
                            self.frameCounter = 0
                            self.resendCommand = False
                    else:
                        msg = self.SendIdle()
                        if(self.commandInQueue != None):
                            state=Payload(data)
                            msg = self.ProcessCommand(state)
                    if(msg==None):
                        msg=self.SendIdle()
                    connection.sendall(msg.encode('utf-8'))
                    if(self.commandInQueue != None and self.commandSent == True and
                    self.resendCommand == False):
                        self.commandInQueue = None
                        self.commandSent = False
                else:
                    break

            print('sending data back to the client')

            connection.close()
        finally:
            # Clean up the connection
            print('closing the connection')
            connection.close()

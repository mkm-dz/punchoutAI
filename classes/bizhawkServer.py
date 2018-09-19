import socket
import sys
import time
import json
from classes.runner import RunWrapper

class Payload(object):
    def __init__(self, j):
            self.__dict__ = json.loads(j)

class BizHawkServer:
    template='{"p1":{"Up":%s,"Down":false,"Left":%s,"Right":false,"Start":false,"Select":false,"B":%s,"A":false},"p2":{},"type":"%s","savegamepath":"c:\\\\users\\\\vidal\\\\Desktop\\\\punchOut.state"}'

    hit = False
    processing = False
    healthP1 = 100
    healthP2 = 100
    sock = None
    commandInQueue = None
    runner=None

    def __init__(self, runner: RunWrapper):
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
    
    def ProcessState(self, deserializedObject):
        deltaHealth = self.healthP1-deserializedObject.p1.health
        if deltaHealth > 0:
            self.healthP1=self.healthP1-deltaHealth
            self.hit=True
        runner.SendData()

    def SendIdle(self, connection) -> str:
        formattedTemplate = self.template % (False,False,False,'processing')
        return formattedTemplate

    def mainLoop(self):
        # Wait for a connection
        print('waiting for a connection')
        counter=0
        connection, client_address = self.sock.accept()

        try:
            print('connection from %s' % client_address[0])
            counter=0
            frameSkip=0
            while True:
                pressed="false"
                commandType="buttons"
                data = connection.recv(1024).decode()
                if data:
                    msg = SendIdle()
                    if(self.commandInQueue != None):
                        msg=ProcessState(Payload(data))

                    connection.sendall(msg.encode('utf-8'))
                    #  if ((counter % 150) == 0 ) or (frameSkip < 6 and frameSkip > 0):
                    #      pressed="true"
                    #      holdingUp="false"
                    #      frameSkip=frameSkip+1
                    #      counter=0
                    #  else:
                    #      pressed="false"
                    #      frameSkip=0
                    #      holdingUp="true"
                    #  deserializedObject = Payload(data)
                    #  print('received "%s"' % data)
                    #  if deserializedObject.round_over == True:
                    #     commandType="reset"
                    #  else:
                    #      commandType="false"
                    #  formattedTemplate = template % (holdingUp,pressed,pressed,commandType)
                    #  

                else:
                    break

            print('sending data back to the client')
            
            connection.close()
        finally:
            # Clean up the connection
            print('closing the connection')
            connection.close()

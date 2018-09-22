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
    template='{"p1":{"Up":%s,"Down":%s,"Left":%s,"Right":%s,"Start":false,"Select":false,"B":%s,"A":%s},"p2":{},"type":"%s","savegamepath":"c:\\\\users\\\\vidal\\\\Desktop\\\\punchOut.state"}'

    hit = False
    processing = False
    healthP1 = 100
    healthP2 = 100
    sock = None
    commandInQueue = None
    buttons=None
    runner=None
    frameCounter=0
    msg=None

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

    def SetButtons(self, up,down,left,right,a,b):
        #This is the javascript way not the python way.
        self.buttons= { 'up':up,
                        'down':down,
                        'left':left,
                        'right':right,
                        'a':a,
                        'b':b }

    def SendIdle(self) -> str:
        formattedTemplate = self.template % (False,False,False,False,False,False,'processing')
        return formattedTemplate
    
    def SendStateToEmulator(self, command: str)->str:
        formattedTemplate = self.template % (self.buttons.up,self.buttons.down,self.buttons.left,self.buttons.right,self.buttons.a,self.buttons.b, command)
        return formattedTemplate
    
    def ProcessCommand(self):
    # deltaHealth = self.healthP1-deserializedObject.p1.health
    # if deltaHealth > 0:
    #     self.healthP1=self.healthP1-deltaHealth
    #     self.hit=True
    # self.runner.SendData()
        if(self.commandInQueue == 'GetState'):
            pass
        if(self.commandInQueue == 'SendState'):
            return SendStateToEmulator('buttons')
        return SendIdle()

    def run(self):
        # Wait for a connection
        print('waiting for a connection')
        counter=0
        connection, client_address = self.sock.accept()

        try:
            print('connection from %s' % client_address[0])
            counter=0
            frameSkip=0
            while True:
                data = connection.recv(1024).decode()
                if data:
                    frameCounter+=1
                    if(frameCounter == 5000):
                        frameCounter = 0

                    if(frameCounter % 5)!=0:
                        # envia el ultimo mensaje 5 veces
                        print('received "%s"' % data)
                    else:
                        msg = SendIdle()
                        if(self.commandInQueue != None):
                            Payload(data)
                            msg=ProcessCommand()

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

import socket
import sys
import time
import json

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 9999)
print('starting up on %s port %s' % server_address)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

class Payload(object):
         def __init__(self, j):
            self.__dict__ = json.loads(j)

 # Wait for a connection
print('waiting for a connection')
counter=0
connection, client_address = sock.accept()
template='{"p1":{"Up":%s,"Down":false,"Left":%s,"Right":false,"Start":false,"Select":false,"B":%s,"A":false},"p2":{},"type":"%s","savegamepath":"c:\\\\users\\\\vidal\\\\Desktop\\\\punchOut.state"}'
try:
    print('connection from %s' % client_address[0])
    counter=0
    frameSkip=0
    while True:
        counter=counter+1
        pressed="false"
        holdingUp="true"
        commandType="buttons"
        data = connection.recv(1024).decode()
        if data:
             if ((counter % 150) == 0 ) or (frameSkip < 6 and frameSkip > 0):
                 pressed="true"
                 holdingUp="false"
                 frameSkip=frameSkip+1
                 counter=0
             else:
                 pressed="false"
                 frameSkip=0
                 holdingUp="true"
             deserializedObject = Payload(data)
             print('received "%s"' % data)
             if deserializedObject.round_over == True:
                commandType="reset"
             else:
                 commandType="false"
             formattedTemplate = template % (holdingUp,pressed,pressed,commandType)
             connection.sendall(formattedTemplate.encode('utf-8'))

        else:
            break

    print('sending data back to the client')
    
    connection.close()
finally:
    # Clean up the connection
    print('closing the connection')
    connection.close()

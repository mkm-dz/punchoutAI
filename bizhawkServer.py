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
try:
    print('connection from %s' % client_address[0])
    while True:
        data = connection.recv(1024).decode()
        if data:
             deserializedObject = Payload(data)
             print('received "%s"' % data)
             if deserializedObject.round_over == True:
                connection.sendall(
        '{"p1":{"Up":false,"Down":false,"Left":true,"Right":false,"Start":false,"Select":false,"B":true,"A":false},"p2":{},"type":"reset","savegamepath":"c:\\\\users\\\\vidal\\\\Desktop\\\\punchOut.state"}'.encode('utf-8'))
             else:
                 counter=counter+1
                 connection.sendall(
        '{"p1":{"Up":false,"Down":false,"Left":true,"Right":false,"Start":false,"Select":false,"B":true,"A":false},"p2":{},"type":"buttons","savegamepath":"c:\\\\users\\\\vidal\\\\Desktop\\\\punchOut.state"}'.encode('utf-8'))

        else:
            break

    print('sending data back to the client')
    
    connection.close()
finally:
    # Clean up the connection
    print('closing the connection')
    connection.close()

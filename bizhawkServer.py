import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 9999)
print('starting up on %s port %s' % server_address)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

 # Wait for a connection
print('waiting for a connection')
connection, client_address = sock.accept()
try:
    print('connection from %s' % client_address[0])
    while True:
        data = connection.recv(1024).decode()
        if data:
             print('received "%s"' % data)
             connection.sendall(
        '{"p1":{},"p2":{},"type":"reset","player_count":1,"savegamepath":"c:\\\\users\\\\vidal\\\\Desktop\\\\test.state"}'.encode('utf-8'))
        else:
            break

    print('sending data back to the client')
    
    connection.close()
finally:
    # Clean up the connection
    print('closing the connection')
    connection.close()

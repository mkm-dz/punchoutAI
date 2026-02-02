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
    publicState = None
    ready = False
    def __init__(self):
        threading.Thread.__init__(self)
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow socket reuse and disable Nagle's algorithm for lower latency
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        # Bind the socket to the port
        server_address = ('localhost', 9999)
        self.sock.bind(server_address)

        # Listen for incoming connections
        self.sock.listen(10)

    def listenToClient(self, client, address):
        buffer = ""
        while True:
            data = client.recv(2048)
            if data:
                buffer += data.decode()
                # Process complete messages (delimited by newline)
                while "\n" in buffer:
                    message, buffer = buffer.split("\n", 1)
                    if message.strip():
                        state = Payload(message)
                        self.publicState = state
            else:
                break

    def run(self):
        # Wait for a connection
        self.ready = True
        while True:
            client, address = self.sock.accept()
            client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            t = threading.Thread(target = self.listenToClient, args = (client,address))
            t.daemon = True  # Allow clean shutdown
            t.start()


# if __name__ == "__main__":
#     program = BizHawkServer()
#     program.run()


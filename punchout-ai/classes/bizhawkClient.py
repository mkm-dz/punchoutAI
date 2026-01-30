import socket
import sys
import time
import json
import threading

class Payload(object):
    def __init__(self, j):
            self.__dict__ = json.loads(j)


class BizHawkClient():
    template = '{"p1":{"Up":%s,"Down":%s,"Left":%s,"Right":%s,"Start":%s,"Select":false,"B":%s,"A":%s},"p2":{},"type":"%s","timing":"%s","savegamepath":"d:\\\\documents\\\\Documentation\\\\punchOut\\\\punchOut1.state"}'

    server_address = None
    hit = False
    healthP1 = 100
    healthP2 = 100
    sock = None
    buttons = None
    _connected = False

    def __init__(self):
        # Bind the socket to the port
        self.server_address = ('localhost', 9998)
        self.sock = None
        self._connected = False

    def _ensure_connected(self):
        """Ensure we have a valid connection, reconnect if needed"""
        if self.sock is None or not self._connected:
            # Clean up old socket if exists
            if self.sock is not None:
                try:
                    self.sock.close()
                except:
                    pass
            
            # Create new socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.sock.connect(self.server_address)
            self._connected = True

    def _SendCommandToEmulator(self, command: str)->str:
        formattedTemplate = self.template % (
            self.buttons['Up'], self.buttons['Down'], self.buttons['Left'], self.buttons['Right'],
            self.buttons['Start'], self.buttons['B'], self.buttons['A'], command, self.buttons['Timing'])
        return formattedTemplate

    def Send(self, command: str):
        """Send command to emulator, with auto-reconnection on failure"""
        try:
            self._ensure_connected()
            if command is not None:
                msg = self._SendCommandToEmulator(command)
                self.sock.sendall(msg.encode('utf-8'))
        except (socket.error, OSError) as e:
            # Connection lost, mark as disconnected and retry once
            self._connected = False
            try:
                self._ensure_connected()
                if command is not None:
                    msg = self._SendCommandToEmulator(command)
                    self.sock.sendall(msg.encode('utf-8'))
            except:
                raise

    def close(self):
        """Clean up the connection"""
        if self.sock is not None:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
            except:
                pass
            self.sock = None
            self._connected = False

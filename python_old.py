import sys
import time
import socket
import json

# with open('command.txt', 'r') as f:
#     aa = f.readlines()

MSGLEN = 4096
# START_MISSION = 'START-MISSION {"metadata":{"container_id":"1","item_ids":[1,2,3]},"item":{"dimensions":[2500,1500,3000],"weight":10},"pick":{"location":{"zone":1,"container":{"width":2500,"height":1500,"depth":1000,"subdivisions":{"width":4,"height":2}},"position":{"x":0,"y":1,"index":4}},"qty":1},"identify":{"location":{"zone":1,"container":{"width":2500,"height":1500,"depth":1000,"subdivisions":{"width":4,"height":2}},"position":{"x":0,"y":1,"index":4}},"pause":true},"place":{"locations":[{"zone":1,"container":{"width":2500,"height":1500,"depth":1000,"subdivisions":{"width":4,"height":2}},"position":{"x":0,"y":1,"index":4}}]}}'
START_INITIALIZATAION = 'START-INITIALIZATION'
START_MISSION = 'START-MISSION'
INITIALIZING = 'INITIALIZING'
UNINITIALIZED = 'UNINITIALIZED'
WAITING = 'WAITING'

class MySocket:
    """demonstration class only
      - coded for clarity, not efficiency
    """
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.connect('localhost', 2687)

    def connect(self, host, port):
        self.sock.connect((host, port))

    def mysend(self, msg):
        sent = self.sock.send(msg + b'\n')
        if sent == 0:
            raise RuntimeError("socket connection broken")

    def myreceive(self):
        buffer = []
        while True:
            try:
                reply = self.sock.recv(1)
                if not reply:
                    break

                if b'\n' == reply:
                    break
                buffer.append(reply.decode())
            except Exception as e:
                print(e)

        return buffer

def checkStatus(receive=None):
    if receive is not None:
        try:
            if json.loads(receive[0])['system']['status'] == UNINITIALIZED \
                    or json.loads(receive[0])['command']['status'] == WAITING:
                return True
        except Exception as e:
            print(e)

if __name__ == "__main__":

    socket = MySocket()
    receive = socket.myreceive()
    print(''.join(receive))

    while True:
        command = input(">> ")
        arguments = command.split(' ')

        if len(arguments) == 1 and arguments[0] == START_INITIALIZATAION:
            if checkStatus(''.join(receive).split('STATUS-UPDATE')[1:]) == True:
                socket.mysend(START_INITIALIZATAION.encode())
                time.sleep(5)
                receive = socket.myreceive()
                print(''.join(receive))
        elif len(arguments) == 2 and arguments[1] == START_MISSION:

            socket.mysend(START_MISSION.encode())
            time.sleep(5)
            receive = socket.myreceive()
            print(''.join(receive))


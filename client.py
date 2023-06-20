import sys
import time
import socket
import json
import re

START_INITIALIZATAION = 'START-INITIALIZATION'
START_MISSION = 'START-MISSION'
INITIALIZING = 'INITIALIZING'
UNINITIALIZED = 'UNINITIALIZED'
WAITING = 'WAITING'
ACCEPTED = 'ACCEPTED'
place_count = 0

mission_parameter = {
  "metadata": {
    "container_id": None,
    "item_ids": None
  },
  "item": {
    "dimensions": None,
    "weight": None
  },
  "pick": {
    "location": {
      "zone": None,
      "container": {
        "width": None,
        "height": None,
        "depth": None,
        "subdivisions": {
          "width": None,
          "height": None
        }
      },
      "position": {
        "x": None,
        "y": None,
        "index": None
      }
    },
    "qty": None
  },
  "identify": {
    "location": {
      "zone": None,
      "container": {
        "width": None,
        "height": None,
        "depth": None,
        "subdivisions": {
          "width": None,
          "height": None
        }
      },
      "position": {
        "x": None,
        "y": None,
        "index": None
      }
    },
    "pause": False
  },
  "place": {
    "locations": [
      {
        "zone": None,
        "container": {
          "width": None,
          "height": None,
          "depth": None,
          "subdivisions": {
            "width": None,
            "height": None
          }
        },
        "position": {
          "x": None,
          "y": None,
          "index": None
        }
      }
    ]
  }
}

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

def check_command_status(receive=None):
    if receive is not None:
        try:
            return json.loads(receive[0])['command']['status']
        except Exception as e:
            print(e)

def check_system_status(receive=None):
    if receive is not None:
        try:
            return json.loads(receive[0])['system']['status']
        except Exception as e:
            print(e)

def parse_parameter(param=None):
    for argument in param:
        sub_arguments = re.search('\((.*)\)', argument).group(1)
        sub_sub_arguments = sub_arguments.split(',')
        parent_key = argument[:argument.index("(")]
        recursive_dict(mission_parameter[parent_key], sub_sub_arguments, 2)

def recursive_dict(param=None, sub_arguments=None, level=2):
    global place_count
    for k, v in param.items():
        if type(v) == dict:
            if level < 3:
                level += 1
                param[k] = recursive_dict(v, sub_arguments, level)
            else:
                param[k] = container_value_to_json(find_key(sub_arguments, k), k)
        elif isinstance(v, list) == True and k == 'locations':
            if level < 3:
                level += 1
                if place_count == len(param[k]):
                    param[k].append(recursive_dict(v[0], sub_arguments, level))
                else:
                    param[k][place_count] = recursive_dict(v[0], sub_arguments, level)
                place_count += 1
            else:
                param[k][place_count] = container_value_to_json(find_key(sub_arguments, k), k)
        elif find_key(sub_arguments, k) != False:
            param[k] = find_key(sub_arguments, k)

    return param


def find_key(arguments=None, key=None):
    for argument in arguments:
        lists = argument.split('=')
        if lists[0] == key:
            if key == 'item_ids' or key == 'dimensions':
                return [int(x) for x in lists[1].split('|')]
            elif key == 'container' or key == 'position':
                return lists[1]
            elif key == 'pause':
                return bool(int(lists[1]))

            return int(lists[1])

    return False

def container_value_to_json(data=None, key=None):
    values = data.split('|')
    if len(values) > 0 and key == 'container':
        json = {}

        json['width'] = int(re.search('\d+', values[0]).group())

        if len(values) >= 2:
            json['height'] = int(re.search('\d+', values[1]).group())

        if len(values) >= 3:
            json['depth'] = int(re.search('\d+', values[2]).group())

        if len(values) >= 4:
            json['subdivisions'] = {}
            json['subdivisions']['width'] = int(re.search('\d+', values[3]).group())

        if len(values) >= 5:
            json['subdivisions']['height'] = int(re.search('\d+', values[4]).group())

        return json

    if len(values) > 0 and key == 'position':
        json = {}

        json['x'] = int(re.search('\d+', values[0]).group())

        if len(values) >= 2:
            json['y'] = int(re.search('\d+', values[1]).group())

        if len(values) >= 3:
            json['index'] = int(re.search('\d+', values[2]).group())

        return json

    if len(values) > 0 and key == 'item_ids':
        return values

    return None

if __name__ == "__main__":
    socket = MySocket()

    while True:
        command = input(">> ")
        arguments = command.split(' ')

        if len(arguments) == 1 and arguments[0] == START_INITIALIZATAION:
            receive = socket.myreceive()
            print(''.join(receive))
            if check_command_status(''.join(receive).split('STATUS-UPDATE')[1:]) == WAITING\
                    and check_system_status(''.join(receive).split('STATUS-UPDATE')[1:]) == UNINITIALIZED:
                socket.mysend(command.encode())
                time.sleep(5)
        elif arguments[0] == START_MISSION:
            while True:
                receive = socket.myreceive()
                print(''.join(receive))

                if check_command_status(''.join(receive).split('STATUS-UPDATE')[1:]) == ACCEPTED \
                        and check_system_status(''.join(receive).split('STATUS-UPDATE')[1:]) == WAITING:
                    parse_parameter(arguments[1:])
                    socket.mysend(b'START-MISSION ' + json.dumps(mission_parameter).encode())
                    time.sleep(5)
                    break
        else:
            print('Invalid command')
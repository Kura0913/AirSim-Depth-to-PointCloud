import socket 
import json
import sys

BUFFER_SIZE = 65535


class SocketClient:
    def __init__(self, host, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.client_socket.connect((host, port))
    # send command to server
    def send_command(self, command, parameters):
        send_data = {'command': command, 'parameters': parameters}
        print(f"parameters\' size:{sys.getsizeof(json.dumps(send_data).encode())}")
        self.client_socket.send(json.dumps(send_data).encode())
        print(f"The client sent data => {send_data}")
    # wait response from server
    def wait_response(self):
        data = self.client_socket.recv(BUFFER_SIZE)
        raw_data = data.decode()
        print(f"The client received data => {raw_data}")
        
        return json.loads(raw_data)
